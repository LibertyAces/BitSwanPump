import json
import typing

import asyncio

from .sink import KafkaSink


class KafkaBatchSink(KafkaSink):
	"""
	KafkaBatchSink is a sink processor that forwards the event to
	an Apache Kafka specified by a KafkaConnection object in batches.

	It is a proof of concept sink, that allows faster processing of events in the pipeline,
	but does not guarantee processing of all events in situations when the pump is closed etc.

	There is a work to be done with cooperation with aiokafka, so the send_and_wait method works
	properly and is able to send events in batches.
	"""

	ConfigDefaults = {
		"batch_size": 10000,
	}

	def __init__(self, app, pipeline, connection, key_serializer=None, id=None, config=None):
		super().__init__(app, pipeline, connection, key_serializer, id, config)
		self._batch_size = int(self.Config["batch_size"])
		self._throttled = False

	def process(self, context, event: typing.Union[dict, str, bytes]):
		if type(event) == dict:
			event = json.dumps(event)
			event = event.encode(self.Encoding)
		elif type(event) == str:
			event = event.encode(self.Encoding)
		kafka_topic = context.get("kafka_topic", self.Topic)
		kafka_key = context.get("kafka_key")

		if self._key_serializer is not None and kafka_key is not None:
			kafka_key = self._key_serializer(kafka_key)

		self._output_queue.put_nowait((kafka_topic, event, kafka_key))

		if not self._throttled and self._output_queue.qsize() >= self._output_queue_max_size:
			self.Pipeline.throttle(self, True)
			self._throttled = True

	async def _connection(self):
		producer = await self.Connection.create_producer(**self._producer_params)
		try:
			await producer.start()
			while True:
				futures = []
				iterations = 0
				while iterations < self._batch_size:
					iterations = iterations + 1
					topic, message, kafka_key = await self._output_queue.get()

					if topic is None and message is None:
						continue
					future = await producer.send(topic, message, key=kafka_key)
					futures.append(future)

					if self._throttled and self._output_queue.qsize() < self._output_queue_max_size:
						self.Pipeline.throttle(self, False)
						self._throttled = False

				if futures:
					await asyncio.gather(*futures)

		finally:
			await producer.stop()
