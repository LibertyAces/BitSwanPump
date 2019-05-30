import bspump


class KafkaKeyFilter(bspump.Processor):
	"""
	KafkaKeyFilter reduces the incoming event stream from Kafka based on a
	key provided in each event.

	Every Kafka message has a key, KafkaKeyFilter selects only those events where
	the key matches selected "filter_key", other events will be discarded. You may set `filter_key`
	as a processor parameter.

	KafkaKeyFilter	 is meant to be inserted after KafkaSource in a Pipeline.
	"""

	def __init__(self, app, pipeline, key, id=None, config=None):
		self.key = key.encode()
		super().__init__(app, pipeline, id, config)

	def process(self, context, event):
		kafka_ctx = context.get("kafka")
		assert (kafka_ctx is not None)

		key = context.get("kafka").key
		if key is not None and key == self.key:
			return event
		else:
			return None
