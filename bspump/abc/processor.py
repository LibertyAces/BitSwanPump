import asab


class ProcessorBase(asab.ConfigObject):
	"""
	Description:

	|

	"""


	def __init__(self, app, pipeline, id=None, config=None):
		"""
		Initialize method

		**Parameters**

		app : object
			Application object.

		pipeline : Pipeline
			Pipeline.

		id : str, default=None,
			ID of the class of config.

		config : JSON, or other compatible formats, default=None
			Configuration file.


		"""
		super().__init__("pipeline:{}:{}".format(pipeline.Id, id if id is not None else self.__class__.__name__), config=config)

		self.App = app
		self.Loop = app.Loop

		self.Id = id if id is not None else self.__class__.__name__
		self.Pipeline = pipeline


	def time(self):
		"""
		Accurate representation of a time in the pipeline.

		:return: App.time()

		"""
		return self.App.time()


	@classmethod
	def construct(cls, app, pipeline, definition: dict):
		"""
		Can construct a processor based on a specific definition. For example, a JSON file.

		**Parameters**

		app : str
			ID of the app.

		pipeline : str
			ID of the pipeline.

		definition : dict
			Set of instructions based on which processor can be constructed.


		:return: cls(app, pipeline, id=newid, config=config)

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
		Can be implemented to return event based on a given logic.

		**Parameters**

		context :
			Additional information passed to the method.

		event : Data with time stamp stored in any data type, usually it is in JSON.
			You can specify an event that is passed to the method.

		"""
		raise NotImplementedError()


	def locate_address(self):
		"""
		Returns an ID of a processor and a pipeline.

		:return: ID of the pipeline and self.Id.

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
	Inherits from ProcessorBase.

	|

	"""
	pass

