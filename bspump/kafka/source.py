import asyncio
import logging

import confluent_kafka

from ..abc.source import Source

#

L = logging.getLogger(__name__)

#


class KafkaSource(Source):
	"""
	KafkaSource object consumes messages from an Apache Kafka system, which is configured in the KafkaConnection object.
	It then passes them to other processors in the pipeline.

.. code:: python

	class KafkaPipeline(bspump.Pipeline):

			def __init__(self, app, pipeline_id):
					super().__init__(app, pipeline_id)
					self.build(
							bspump.kafka.KafkaSource(app, self, "KafkaConnection", config={'topic': 'messages'}),
							bspump.kafka.KafkaSink(app, self, "KafkaConnection", config={'topic': 'messages2'}),
					)

	To ensure that after restart, pump will continue receiving messages where it left of, group_id has to
	be provided in the configuration.

	When the group_id is set, the consumer group is created and the Kafka server will then operate
	in the producer-consumer mode. It means that every consumer with the same group_id will be assigned
	unique set of partitions, hence all messages will be divided among them and thus unique.

	Long-running synchronous operations should be avoided or places inside the OOBGenerator in the asynchronous
	way or on thread using ASAB Proactor service (see bspump-oob-proactor.py example in "examples" folder).
	Otherwise, the session_timeout_ms should be raised to prevent Kafka from disconnecting the consumer
	from the partition, thus causing rebalance.

	Standard Kafka configuration options can be used,
	as specified in librdkafka library,
	where the options are simply passed to:

	https://github.com/edenhill/librdkafka/blob/master/CONFIGURATION.md
	"""

	ConfigDefaults = {
		"topic": "unconfigured",
		"refresh_topics": 0,
		# In Kafka, the poll interval refers to the frequency at which a consumer polls the Kafka broker for new messages.
		# This interval is crucial because it impacts how the consumer interacts with Kafka in terms of fetching messages,
		# managing offsets, and maintaining group membership.
		# For a consumer subscribed to 15+ topics, a good starting point for the poll interval would be between 0.5 to 1 second.
		# This range provides a balance between responsiveness and resource utilization.
		# If the total number of partitions is very high and/or if the message production rate is significant, you might need to lean towards the lower end of the recommended range (e.g., 0.5 seconds)
		# or even slightly below, but not too much to avoid excessive overhead.
		"poll_interval": 0.5,
		"buffer_size": 1000,
		"buffer_timeout": 1.0,

		# Storage of the offset is done manually after the buffer of messages is processed
		"enable.auto.offset.store": "false",
		"enable.auto.commit": "false",

		"auto.commit.interval.ms": "1000",
		"auto.offset.reset": "smallest",
		"group.id": "bspump",
	}

	def __init__(self, app, pipeline, connection, id=None, config=None):
		"""
		Initializes parameters.

		**Parameters**

		app : Application
				Name of the `Application <https://asab.readthedocs.io/en/latest/asab/application.html#>`_.

		pipeline : Pipeline
				Name of the Pipeline.

		connection : Connection
				information needed to create a connection.

		id : , default = None

		config : , default = None

		"""
		super().__init__(app, pipeline, id=id, config=config)

		self.App = app
		self.Connection = self.Pipeline.locate_connection(app, connection)

		# Sleep time after an error
		# The following value should be the same in every deployment/environment
		self.Sleep = 100 / 1000.0

		# Polling too frequently (e.g., every 0.1 seconds) can introduce significant overhead.
		# Each poll involves network calls and resource utilization on both the consumer and broker side.
		# This can lead to higher CPU and network usage without substantial benefits if the message production
		# rate is not high enough to justify such frequent polls.
		# A 0.5-second poll interval strikes a better balance between responsiveness and resource utilization.
		# It is frequent enough to ensure that the consumer remains active, heartbeats are sent regularly,
		# and messages are fetched in a timely manner. At the same time, it avoids the excessive overhead associated with
		# very frequent polling.
		self.PollInterval = float(self.Config.pop("poll_interval", 0.5))

		# Size of the buffer of consumed messages
		self.BufferSize = int(self.Config.pop("buffer_size", 1000))
		# Timeout of the buffer if consumed messages size is not reached
		self.BufferTimeout = float(self.Config.pop("buffer_timeout", 1.0))  # seconds

		self.ConsumerConfig = {}
		self.SpecialKeys = frozenset(["oauth_cb"])

		# Copy connection options
		for key, value in self.Connection.Config.items():

			if key in self.SpecialKeys:
				self.ConsumerConfig[key] = value

			else:
				self.ConsumerConfig[key.replace("_", ".")] = value

		# Copy configuration options, avoid the topic
		for key, value in self.Config.items():

			if key in ["topic", "refresh_topics"]:
				continue

			if key in self.SpecialKeys:
				self.ConsumerConfig[key] = value

			else:
				self.ConsumerConfig[key.replace("_", ".")] = value

		# Simple asserts can be removed after Python optimization,
		# so we use `if statement` here instead
		if "bootstrap.servers" not in self.ConsumerConfig:
			raise RuntimeError("Missing configuration option: [kafka] bootstrap_servers.")

		# Create subscription list
		self.Subscribe = []

		for s in self.Config['topic'].split(' '):
			if ':' not in s:
				self.Subscribe.append(s)
			else:
				self.Subscribe.append(s.rsplit(':', 1))

		self.Running = True

		# For refreshing of topics/subscription
		self.RefreshTopics = int(self.Config["refresh_topics"])
		self.LastRefreshTopicsTime = self.App.time()

		# To run the poll on a separate thread
		self.ProactorService = app.get_service("asab.ProactorService")
		self.Buffer = []
		self.BufferLock = asyncio.Lock()
		self.LastFlushTime = self.App.time()
		self.Loop = asyncio.get_event_loop()


	def poll_kafka(self, consumer):
		"""
		This method runs on a thread and fills the buffer with the polled messages from the Kafka consumer.

		Running Kafka's poll method on a separate thread in an asynchronous application enhances responsiveness
		by freeing the main thread for other tasks. It ensures non-blocking processing, improving throughput and
		scalability, as message fetching and processing are decoupled.
		This approach also optimizes resource utilization by leveraging multiple CPU cores and enhances error
		handling, making the application more resilient and maintainable.
		"""
		while self.Running:
			current_time = self.App.time()

			if self.RefreshTopics > 0 and current_time > self.LastRefreshTopicsTime + self.RefreshTopics:
				L.info("Topics refreshed in '{}'.".format(self.Id))
				consumer.unsubscribe()
				self.LastRefreshTopicsTime = current_time
				return

			m = consumer.poll(self.PollInterval)

			if m is None:
				continue

			if m.error():
				L.error("The following error occurred while polling for messages: '{}'.".format(m.error()))
				consumer.unsubscribe()
				return

			self.Buffer.append(m)

			if len(self.Buffer) >= self.BufferSize or (current_time - self.LastFlushTime) > self.BufferTimeout:

				try:
					future = asyncio.run_coroutine_threadsafe(self.flush_buffer(consumer), self.Loop)
					# Wait for the result:
					future.result()

				except Exception as e:
					L.exception("The following error occurred while processing batch of Kafka messages: '{}'.".format(e))

				self.LastFlushTime = self.App.time()


	async def flush_buffer(self, consumer):
		"""
		This method flushes the buffer to the pipeline.
		It should be thread safe.
		"""

		if self.BufferLock.locked():
			return

		async with self.BufferLock:

			if self.Buffer:
				messages = self.Buffer

				if len(messages) == 0:
					return

				self.Buffer = []

				for m in messages:
					await self.process(m.value(), context={
						"kafka_key": m.key(),
						"kafka_headers": m.headers(),
						"_kafka_topic": m.topic(),
						"_kafka_partition": m.partition(),
						"_kafka_offset": m.offset(),
					})

					# Store the offset associated with msg to a local cache.
					# Stored offsets are committed to Kafka by a background thread every 'auto.commit.interval.ms'.
					# Explicitly storing offsets after processing gives at-least once semantics.
					try:

						if consumer:
							consumer.store_offsets(m)

					except confluent_kafka.KafkaException as err:

						# Reballacing of partitions happened during consuming,
						# so this consumer no longer owns the partition
						# -> let the other consumer consume the events and here just finish
						# https://medium.com/@a.a.halutin/simple-examples-with-confluent-kafka-9b7e58534a88
						if err.args[0].code() == confluent_kafka.KafkaError._STATE and err.args[0].val() == -172:
							break

						L.warning("The following warning occurred inside Kafka consumer: '{}'".format(err))
						break

					except RuntimeError as e:
						L.exception("Error storing offsets, possible consumer state issue: '{}'".format(e))
						break

				# Manually commit the offsets after processing the batch
				try:

					if consumer:
						consumer.commit(asynchronous=False)  # Commit offsets synchronously

				except confluent_kafka.KafkaException as e:
					L.exception("Failed to commit offsets: '{}'".format(e))


	async def main(self):

		while self.Running:

			try:
				c = confluent_kafka.Consumer(self.ConsumerConfig, logger=L)

			except BaseException as e:
				L.exception("Error when connecting to Kafka")
				self.Pipeline.set_error(None, None, e)
				return

			c.subscribe(self.Subscribe)

			try:
				# Run the poll loop on a separate thread
				await self.ProactorService.execute(self.poll_kafka, c)

			except asyncio.CancelledError:
				self.Running = False

			except BaseException as e:
				L.exception("Error when processing Kafka message")
				self.Pipeline.set_error(None, None, e)

			finally:

				# Flush remaining messages in buffer before exiting
				await self.flush_buffer(c)

				# Close the consumer
				if c:
					c.close()

				await asyncio.sleep(self.Sleep)  # Prevent tight loop on errors
