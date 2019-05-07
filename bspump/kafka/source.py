import re
import logging
import aiokafka
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

    """

	ConfigDefaults = {
		'topic': '', # Multiple values are allowed, separated by , character
		'client_id': 'BSPump-KafkaSource',
		'group_id': '',
		'max_partition_fetch_bytes': 1048576,
		'auto_offset_reset': 'earliest',
		'api_version': 'auto', # or e.g. 0.9.0
		'retry': 20,
	}


	def __init__(self, app, pipeline, connection, id=None, config=None):
		super().__init__(app, pipeline, id=id, config=config)

		self.topics = re.split(r'\s*,\s*', self.Config['topic'])

		self._group_id = self.Config['group_id']
		if len(self._group_id) == 0: self._group_id = None

		self.Connection = pipeline.locate_connection(app, connection)
		self.App = app
		self.Consumer = aiokafka.AIOKafkaConsumer(
			*self.topics,
			loop = self.App.Loop,
			bootstrap_servers = self.Connection.get_bootstrap_servers(),
			client_id = self.Config['client_id'],
			group_id = self._group_id,
			max_partition_fetch_bytes = int(self.Config['max_partition_fetch_bytes']),
			auto_offset_reset = self.Config['auto_offset_reset'],
			api_version = self.Config['api_version'],
			enable_auto_commit=False
		)
		self.Partitions = None
		self.Retry = int(self.Config['retry'])
		self.Pipeline = pipeline


	async def main(self):
		await self.Consumer.start()
		self.Partitions = self.Consumer.assignment()
		try:
			while 1:
				await self.Pipeline.ready()
				data = await self.Consumer.getmany(timeout_ms=20000)
				if len(data) == 0:
					for partition in self.Partitions:
						await self.Consumer.seek_to_end(partition)
					data = await self.Consumer.getmany(timeout_ms=20000)
				
				for tp, messages in data.items():
					for message in messages:
						#TODO: If pipeline is not ready, don't commit messages ...
						await self.process_message(message)
				
				if self._group_id is not None:
					for i in range(self.Retry, 0, -1):
						try:
							await self.Consumer.commit()
							break
						except Exception as e:
							L.exception("Error {} during Kafka commit - will retry in 5 seconds".format(e))
							await asyncio.sleep(5)
							self.Consumer.subscribe(self.topics)
							self.Partitions = self.Consumer.assignment()
							if i == 1:
								self.Pipeline.set_error(None, None, e)
								return
						
		except concurrent.futures._base.CancelledError:
			pass
		except BaseException as e:
			L.exception("Error when processing Kafka message")
		finally:
			await self.Consumer.stop()


	async def process_message(self, message):
		context = { "kafka": message }
		await self.process(message.value, context=context)
