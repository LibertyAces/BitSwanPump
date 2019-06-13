import bspump


class KafkaKeyFilter(bspump.Processor):
	"""
	KafkaKeyFilter reduces the incoming event stream from Kafka based on a
	key provided in each event.

	Every Kafka message has a key, KafkaKeyFilter selects only those events where
	the key matches selected "filter_key", other events will be discarded. You may set filtering `key`
	as a processor parameter (bytes).

	KafkaKeyFilter	 is meant to be inserted after KafkaSource in a Pipeline.
	"""

	def __init__(self, app, pipeline, keys, id=None, config=None):
		super().__init__(app, pipeline, id, config)
		if isinstance (keys,list):
			self._keys = keys
			self.process = self.process_keys
		else:
			self._key = keys
			self.process = self.process_key

	def process (self, context, event):
		pass

	def process_key(self, context, event):
		kafka_ctx = context.get("kafka")
		assert (kafka_ctx is not None)

		key = kafka_ctx.key
		if key is not None and key == self._key:
			return event
		else:
			return None

	def process_keys(self, context, event):
		kafka_ctx = context.get("kafka")
		assert (kafka_ctx is not None)

		key = kafka_ctx.key
		if key is not None and key in self._keys:
			return event
		else:
			return None


	# simple version

	# def __init__(self, app, pipeline, keys, id=None, config=None):
	# 	super().__init__(app, pipeline, id, config)
	# 	if not isinstance (keys,list):
	# 		self._keys = [keys]
	# 	else:
	# 		self._keys = keys
	#
	#
	#
	# def process(self, context, event):
	# 	kafka_ctx = context.get("kafka")
	# 	assert (kafka_ctx is not None)
	#
	# 	key = kafka_ctx.key
	# 	if key is not None and key in self._keys:
	# 		return event
	# 	else:
	# 		return None
