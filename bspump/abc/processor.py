import asab


class ProcessorBase(asab.ConfigObject):
	"""
	test comment
	"""

	def __init__(self, app, pipeline, id=None, config=None):
		super().__init__("pipeline:{}:{}".format(pipeline.Id, id if id is not None else self.__class__.__name__), config=config)

		self.App = app
		self.Loop = app.Loop

		self.Id = id if id is not None else self.__class__.__name__
		self.Pipeline = pipeline


	def time(self):
		return self.App.time()


	@classmethod
	def construct(cls, app, pipeline, definition: dict):
		newid = definition.get('id')
		config = definition.get('config')
		args = definition.get('args')
		if args is not None:
			return cls(app, pipeline, id=newid, config=config, **args)
		else:
			return cls(app, pipeline, id=newid, config=config)


	def process(self, context, event):
		"""
		process is a method which...
		"""
		raise NotImplementedError()


	def locate_address(self):
		return "{}.{}".format(self.Pipeline.Id, self.Id)


	def rest_get(self):
		return {
			"Id": self.Id,
			"Class": self.__class__.__name__,
			"PipelineId": self.Pipeline.Id,
		}


	def __repr__(self):
		return '%s(%r)' % (self.__class__.__name__, self.locate_address())


class Processor(ProcessorBase):
	"""
		The main component of the BSPump architecture is a so called processor.
		This object modifies, transforms and enriches events.
		Moreover, it is capable of calculating metrics and creating aggregations, detecting anomalies or react to known as well as unknown system behavior patterns.

		Processors differ as to their functions and all of them are aligned according to a predefined sequence in pipeline objects.
		As regards working with data events, each pipeline has its own unique task.
	"""
	pass

