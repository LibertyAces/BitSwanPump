import json
import logging
import typing
import asyncio

from ..abc.sink import Sink

#

L = logging.getLogger(__name__)

#


class KafkaSink(Sink):
	"""
    KafkaSink is a sink processor that forwards the event to a Apache Kafka specified by a KafkaConnection object.

    KafkaSink expects bytes as an input. If the input is string or dictionary, it is automatically transformed to bytes using encoding charset specified in the configuration.
    
.. code:: python

    class KafkaPipeline(bspump.Pipeline):

        def __init__(self, app, pipeline_id):
            super().__init__(app, pipeline_id)
            self.build(
                bspump.kafka.KafkaSource(app, self, "KafkaConnection", config={'topic': 'messages'}),
                bspump.kafka.KafkaSink(app, self, "KafkaConnection", config={'topic': 'messages2'}),
        )

	There are to ways to use KafkaSink:
		 - Specify a single topic in KafkaSink config - topic, to be used for all the events in pipeline.
		 - Specify topic separetly for each event in event context - context['kafk_topic'].
		   Topic from configuration is than used as a default topic.
		   To provide business logic for event distribution, you can create topic selector processor.
	Processor example:

.. code:: python

	class KafkaTopicSelector(bspump.Processor):

		def process(self, context, event):
			if event.get("weight") > 10:
				context["kafka_topic"] = "heavy"
			else:
				context["kafka_topic"] = "light"

			return event


    Every kafka message can be a key:value pair. Key is read from event context - context['kafka_key'].
    If kafka_key is not provided, key defaults to None.

    """

	ConfigDefaults = {
		'topic': '',
		'encoding': 'utf-8',
		'output_queue_max_size': 100,
	}


	def __init__(self, app, pipeline, connection, key_serializer=None, id=None, config=None):
		super().__init__(app, pipeline, id=id, config=config)

		self.Connection = pipeline.locate_connection(app, connection)
		self.Topic = self.Config['topic']
		self._key_serializer = key_serializer
		self.Encoding = self.Config['encoding']

		self._output_queue = asyncio.Queue(loop=app.Loop)
		self._output_queue_max_size = int(self.Config['output_queue_max_size'])
		# TODO: remove - just testing
		self._output_queue_max_size = 1000
		self._conn_future = None

		# Subscription
		self.PubSub = app.PubSub

		self.sink_name = f"{pipeline.Id}:{self.Id}"


		self._on_health_check('connection.open!')
		self.PubSub.subscribe("Application.stop!", self._on_application_stop)
		self.PubSub.subscribe("Application.tick!", self._on_health_check)


	def _on_health_check(self, message_type):
		if self._conn_future is not None:
			# Connection future exists

			if not self._conn_future.done():
				# Connection future didn't result yet
				# No sanitization needed
				return

			try:
				self._conn_future.result()
			except:
				# Connection future threw an error
				L.exception("Unexpected connection future error")

			# Connection future already resulted (with or without exception)
			self._conn_future = None

		assert (self._conn_future is None)

		self._conn_future = asyncio.ensure_future(
			self._connection(),
			loop=self.Loop
		)


	def _on_application_stop(self, message_type, counter):
		self._output_queue.put_nowait((None, None, None))


	async def _connection(self):
		producer = await self.Connection.create_producer()
		try:
			await producer.start()
			await self._loader(producer=producer)
		except BaseException as e:
			L.exception("Unexpected Kafka Error.")
		finally:
			await producer.stop()


	async def _loader(self, producer):
		while True:
			topic, message, kafka_key = await self._output_queue.get()

			if topic is None and message is None:
				break

			if self._output_queue.qsize() == self._output_queue_max_size - 1:
				self.Pipeline.throttle(self, False)

			await producer.send_and_wait(topic, message, key=kafka_key)


	def process(self, context, event:typing.Union[dict, str, bytes]):
		if type(event) == dict:
			event = json.dumps(event)
			event = event.encode(self.Encoding)
		elif type(event) == str:
			event = event.encode(self.Encoding)
		kafka_topic = context.get("kafka_topic", self.Topic)
		kafka_key = context.get("kafka_key")

		# TODO: Make KafkaConnection create separate producer for every sink
		#  	- key/value serialization could be moved there.

		if self._key_serializer is not None and kafka_key is not None:
			kafka_key = self._key_serializer(kafka_key)

		self._output_queue.put_nowait((kafka_topic, event, kafka_key))

		if self._output_queue.qsize() == self._output_queue_max_size:
			self.Pipeline.throttle(self, True)
