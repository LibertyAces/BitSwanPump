import asab


class ProcessorBase(asab.ConfigObject):
	"""
	Description:

	|

	"""


	def __init__(self, app, pipeline, id=None, config=None):
		"""
		Description:

		|

		"""
		super().__init__("pipeline:{}:{}".format(pipeline.Id, id if id is not None else self.__class__.__name__), config=config)

		self.App = app
		self.Loop = app.Loop

		self.Id = id if id is not None else self.__class__.__name__
		self.Pipeline = pipeline


	def time(self):
		"""
		Description:

		:return: time

		|

		"""
		return self.App.time()


	@classmethod
	def construct(cls, app, pipeline, definition: dict):
		"""
		Description:

		**Parameters**

		app : str
			id of the app

		pipeline : str
			id of the pipeline

		definition : dict
			description?


		:return: ??

		|

		"""
		newid = definition.get('id')
		config = definition.get('config')
		args = definition.get('args')
		if args is not None:
			return cls(app, pipeline, id=newid, config=config, **args)
		else:
			return cls(app, pipeline, id=newid, config=config)


	def process(self, context, event):
		"""
		Description:

		**Parameters**

		context : ??
			description??

		event : ??
			description??

		"""
		raise NotImplementedError()


	def locate_address(self):
		"""
		Description:

		:return: ID of the pipeline

		|

		"""
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
	Description:

	|

	"""
	pass

