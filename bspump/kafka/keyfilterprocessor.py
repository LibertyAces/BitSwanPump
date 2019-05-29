import bspump


class KafkaKeyFilterProcessor(bspump.Processor):
	"""
	KafkaKeyFilter reduces the incoming event stream from Kafka based on a
	key provided in each event.

	Every Kafka message has a key, KafkaKeyFilter selects only those events where
	the key matches selected "filter_key", other events will be discarded. You may set `filter_key`
	in processor configuration.

	KafkaKeyFilter	 is meant to be inserted after KafkaSource in a Pipeline.
	"""

	def __init__(self, app, pipeline, id=None, config=None):
		super().__init__(app, pipeline, id, config)

	def process(self, context, event):
		assert context.get("kafka") != None
		assert self.Config.get("filter_key") != None

		key = context.get("kafka").key
		filter_key = self.Config.get("filter_key")
		if key != None and key.decode() == filter_key:
			return event
