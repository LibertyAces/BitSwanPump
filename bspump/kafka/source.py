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
		"enable.auto.commit": "true",
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
		self.Sleep = 100 / 1000.0
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

		assert "bootstrap.servers" in self.ConsumerConfig, "Bootstrap Servers must be set in [kafka] section in the configuration."

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

				while self.Running:

					await self.Pipeline.ready()
					current_time = self.App.time()

					if self.RefreshTopics > 0 and current_time > self.LastRefreshTopicsTime + self.RefreshTopics:
						L.info("Topics refreshed in '{}'.".format(self.Id))
						c.unsubscribe()
						c.close()
						self.LastRefreshTopicsTime = current_time
						break

					m = await self.ProactorService.execute(c.poll, 0.5)  # Increased poll interval

					if m is None:
						await asyncio.sleep(self.Sleep)
						continue

					if m.error():
						L.error("The following error occurred while polling for messages: '{}'.".format(m.error()))
						await asyncio.sleep(self.Sleep)
						c.unsubscribe()
						c.close()
						break

					await self.process(m.value(), context={
						"kafka_key": m.key(),
						"kafka_headers": m.headers(),
						"_kafka_topic": m.topic(),
						"_kafka_partition": m.partition(),
						"_kafka_offset": m.offset(),
					})

			except asyncio.CancelledError:
				self.Running = False

			except BaseException as e:
				L.exception("Error when processing Kafka message")
				self.Pipeline.set_error(None, None, e)

			finally:
				c.close()
				await asyncio.sleep(self.Sleep)  # Prevent tight loop on errors
