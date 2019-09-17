import bspump
import collections.abc


class KafkaKeyFilter(bspump.Processor):
	"""
	KafkaKeyFilter reduces the incoming event stream from Kafka based on a
	key provided in each event.

	Every Kafka message has a key, KafkaKeyFilter selects only those events where
	the event key matches one of provided 'keys', other events will be discarded.

	Set filtering `keys` as a parameter (in bytes) in the KafkaKeyFilter constructor.

	KafkaKeyFilter is meant to be inserted after KafkaSource in a Pipeline.
	"""

	def __init__(self, app, pipeline, keys, id=None, config=None):
		super().__init__(app, pipeline, id, config)
		if not isinstance(keys, collections.abc.Iterable) or isinstance(keys, bytes):
			self.Keys = frozenset([keys])
		else:
			self.Keys = frozenset(keys)



	def process(self, context, event):
		kafka_ctx = context.get("kafka")
		assert (kafka_ctx is not None)

		key = kafka_ctx.key
		if key is not None and key in self.Keys:
			return event
		else:
			return None
