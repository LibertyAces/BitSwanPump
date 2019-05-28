import bspump


class KafkaKeyFilterProcessor(bspump.Processor):

	def __init__(self, app, pipeline, id=None, config=None):
		super().__init__(app, pipeline, id, config)

	def process(self, context, event):
		assert context.get("kafka") != None
		assert self.Config.get("filter_key") != None

		key = context.get("kafka").key
		filter_key = self.Config.get("filter_key")
		if key != None and key.decode() == filter_key:
			return event
