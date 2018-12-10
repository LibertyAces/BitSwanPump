import re
import logging
import aiokafka
import concurrent

from ..abc.source import Source

#

L = logging.getLogger(__name__)

#


class KafkaSource(Source):


	ConfigDefaults = {
		'topic': '', # Multiple values are allowed, separated by , character
		'client_id': 'BSPump-KafkaSource',
		'group_id': '',
		'max_partition_fetch_bytes': 1048576,
		'auto_offset_reset': 'latest',
		'api_version': 'auto', # or e.g. 0.9.0
	}


	def __init__(self, app, pipeline, connection, id=None, config=None):
		super().__init__(app, pipeline, id=id, config=config)

		topics = re.split(r'\s*,\s*', self.Config['topic'])

		self._group_id = self.Config['group_id']
		if len(self._group_id) == 0: self._group_id = None

		self.Connection = pipeline.locate_connection(app, connection)
		self.Consumer = aiokafka.AIOKafkaConsumer(
			*topics,
			loop = app.Loop,
			bootstrap_servers = self.Connection.get_bootstrap_servers(),
			client_id = self.Config['client_id'],
			group_id = self._group_id,
			max_partition_fetch_bytes = int(self.Config['max_partition_fetch_bytes']),
			auto_offset_reset = self.Config['auto_offset_reset'],
			api_version = self.Config['api_version'],
			enable_auto_commit=False
		)


	async def main(self):
		await self.Consumer.start()
		try:
			while 1:
				await self.Pipeline.ready()
				data = await self.Consumer.getmany(timeout_ms=10000)
				for tp, messages in data.items():
					for message in messages:
						#TODO: If pipeline is not ready, don't commit messages ...
						await self.process_message(message)
				if self._group_id is not None:
					await self.Consumer.commit()

		except concurrent.futures._base.CancelledError:
			pass
		except BaseException as e:
			L.exception("Error when processing Kafka message")
		finally:
			await self.Consumer.stop()


	async def process_message(self, message):
		context = { "kafka": message }
		await self.process(message.value, context=context)
