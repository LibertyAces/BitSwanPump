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
		"""
		Initializes variables

		**Parameters**

		app : Application
			Name of the `Application <https://asab.readthedocs.io/en/latest/asab/application.html`_.

		pipeline : Pipeline
			Name of the Pipeline.

		keys : bytes
			keys used to filter out events from the event stream.

		id : , default = None

		config : JSON, default = None
			configuration file in JSON

		"""
		super().__init__(app, pipeline, id, config)
		if not isinstance(keys, collections.abc.Iterable) or isinstance(keys, bytes):
			self.Keys = frozenset([keys])
		else:
			self.Keys = frozenset(keys)



	def process(self, context, event):
		"""
		Does the filtering processed based on passed key variable.

		**Parameters**

		context : Context
			additional information passed to the method

		event : any type,a single unit of information that flows through the Pipeline.

		"""
		kafka_ctx = context.get("kafka")
		assert (kafka_ctx is not None)

		key = kafka_ctx.key
		if key is not None and key in self.Keys:
			return event
		else:
			return None
