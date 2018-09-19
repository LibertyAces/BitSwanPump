import logging
import aiokafka
import concurrent

from ..abc.source import Source

#

L = logging.getLogger(__name__)

#


class KafkaSource(Source):


	ConfigDefaults = {
		'topic': '',
	}


	def __init__(self, app, pipeline, connection, id=None, config=None):
		super().__init__(app, pipeline, id=id, config=config)

		self._connection = pipeline.locate_connection(app, connection)
		self._consumer = aiokafka.AIOKafkaConsumer(
			self.Config['topic'],
			loop=app.Loop,
			bootstrap_servers=self._connection.get_bootstrap_servers()
		)


	async def main(self):
		await self._consumer.start()
		try:
			while 1:
				await self.Pipeline.ready()
				msg = await type(self._consumer).__anext__(self._consumer)
				await self.process_message(msg)
		except StopAsyncIteration:
			pass
		except concurrent.futures._base.CancelledError:
			pass
		except BaseException as e:
			L.exception("Error when processing Kafka message")
		finally:
			await self._consumer.stop()


	async def process_message(self, msg):
		# Expand msg attributes to context
		msg_dict = msg._asdict()
		msg_dict.pop('value')
		context = {
			"kafka": dict(msg_dict)
		}

		# Process
		await self.process(msg.value, context=context)
