import re
import logging

import aiokafka
import kafka
import concurrent
import asyncio

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
    """

	ConfigDefaults = {
		"topic": "", # Multiple values are allowed, separated by , character
		"retry": 20,
		"group_id": "",
		
		"client_id": "BSPump-KafkaSource",

		"auto_offset_reset": "earliest",
		"max_partition_fetch_bytes": "",
		"api_version": "auto",
		
		"session_timeout_ms": "",
		"consumer_timeout_ms": "",
		"request_timeout_ms": "",

		"time_per_event": 1,  # the time after which the main method enters the idle state to allow other operations to perform their tasks
		"event_idle_time": 0.01,  # the time for which the read method enters the idle state (see above)
	}

	def __init__(self, app, pipeline, connection, id=None, config=None):
		super().__init__(app, pipeline, id=id, config=config)

		self.topics = re.split(r'\s*,\s*', self.Config['topic'])


		consumer_params = {}
		
		self._group_id = self.Config.get ("group_id")
		if len (self._group_id) > 0:
			consumer_params['group_id'] = self._group_id

		v = self.Config.get('client_id')
		if v != "": consumer_params['client_id'] = v
		
		v = self.Config.get('auto_offset_reset')
		if v != "": consumer_params['auto_offset_reset'] = v

		v = self.Config.get('api_version')
		if v != "": consumer_params['api_version'] = v
		
		v = self.Config.get('max_partition_fetch_bytes')
		if v != "": consumer_params['max_partition_fetch_bytes'] = int(v)

		v = self.Config.get('session_timeout_ms')
		if v != "": consumer_params['session_timeout_ms'] = int(v)

		v = self.Config.get('consumer_timeout_ms')
		if v != "": consumer_params['consumer_timeout_ms'] = int(v)

		v = self.Config.get('request_timeout_ms')
		if v != "": consumer_params['request_timeout_ms'] = int(v)


		self.Connection = pipeline.locate_connection(app, connection)
		self.App = app

		self.Partitions = None
		self.ConsumerParams = consumer_params
		self.Consumer = None
		self.create_consumer()

		self.Retry = int(self.Config['retry'])
		self.Pipeline = pipeline

		self.LastTime = 0
		self.TimePerEvent = int(self.Config["time_per_event"])
		self.EventIdleTime = float(self.Config["event_idle_time"])

	def create_consumer(self):
		self.Partitions = None
		self.Consumer = self.Connection.create_consumer(
			*self.topics,
			**self.ConsumerParams
		)

	async def initialize_consumer(self):
		await self.Consumer.start()
		self.Partitions = self.Consumer.assignment()

	async def main(self):
		await self.initialize_consumer()
		try:
			while 1:
				await self.Pipeline.ready()
				data = await self.Consumer.getmany(timeout_ms=20000)
				if len(data) == 0:
					for partition in self.Partitions:
						await self.Consumer.seek_to_end(partition)
					data = await self.Consumer.getmany(timeout_ms=20000)
				for topic_partition, messages in data.items():
					for message in messages:
						#TODO: If pipeline is not ready, don't commit messages ...
						await self.simulate_event()
						await self.process_message(message)
				if len(self._group_id) > 0:
					await self._commit()
		except concurrent.futures._base.CancelledError:
			pass
		finally:
			await self.Consumer.stop()

	async def _commit(self):
		for i in range(self.Retry, 0, -1):
			try:
				await self.Consumer.commit()
				self.LastTime = 0
				break
			except concurrent.futures._base.CancelledError as e:
				# Ctrl-C -> terminate and exit
				raise e
			except (
					kafka.errors.IllegalStateError,
					kafka.errors.CommitFailedError,
					kafka.errors.UnknownMemberIdError,
					kafka.errors.NodeNotReadyError,
					kafka.errors.RebalanceInProgressError,
					concurrent.futures.CancelledError,
			) as e:
				# Retry-able errors
				if i == 1:
					L.exception("Error {} during Kafka commit".format(e))
					self.Pipeline.set_error(None, None, e)
					return
				else:
					L.exception("Error {} during Kafka commit - will retry in 5 seconds".format(e))
					await asyncio.sleep(5)
					# TODO: Think about a more elegant way how to stop the consumer
					# TODO: aiokafka does not handle exceptions of its components and thus it cannot be fully stopped via stop
					# TODO: https://github.com/aio-libs/aiokafka/blob/master/aiokafka/consumer/consumer.py#L457
					try:
						await self.Consumer._coordinator.close()
					except Exception as e:
						L.exception("Error {} during closing consumer's coordinator after Kafka commit".format(e))
					try:
						await self.Consumer._fetcher.close()
					except Exception as e:
						L.exception("Error {} during closing consumer's fetcher after Kafka commit".format(e))
					try:
						await self.Consumer._client.close()
					except Exception as e:
						L.exception("Error {} during closing consumer's client after Kafka commit".format(e))
					self.create_consumer()
					await self.initialize_consumer()
			except Exception as e:
				# Hard errors
				L.exception("Error {} during Kafka commit".format(e))
				self.Pipeline.set_error(None, None, e)
				return

	async def simulate_event(self):
		'''
		The simulate_event method should be called in main method after a message has been processed.

		It ensures that all other asynchronous events receive enough time to perform their tasks.
		Otherwise, the application loop is blocked by a file reader and no other activity makes a progress.
		'''

		current_time = self.App.time()
		if self.LastTime == 0:
			self.LastTime = current_time
			return

		if (current_time - self.LastTime) >= self.TimePerEvent:
			if len(self._group_id) > 0:
				await self._commit()
			await asyncio.sleep(self.EventIdleTime)
			self.LastTime = current_time + self.EventIdleTime


	async def process_message(self, message):
		context = { "kafka": message }
		await self.process(message.value, context=context)
