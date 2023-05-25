import asab


class ProcessorBase(asab.Configurable):
	"""
	Description:

	|

	"""


	def __init__(self, app, pipeline, id=None, config=None):
		"""
		Initializes the Parameters

		**Parameters**

		app : object
				Application object.

		pipeline : :meth:`Pipeline <bspump.Pipeline()>`
				Name of the :meth:`Pipeline <bspump.Pipeline()>`.

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
		Accurate representation of a time in the :meth:`Pipeline <bspump.Pipeline()>`.

		:return: App.time()

		"""
		return self.App.time()


	@classmethod
	def construct(cls, app, pipeline, definition: dict):
		"""
		Can construct a :meth:`processor <bspump.Processor()>` based on a specific definition. For example, a JSON file.

		**Parameters**

		app : Application
				Name of the `Application <https://asab.readthedocs.io/en/latest/asab/application.html#>_`.

		pipeline : str
				Name of the :meth:`Pipeline <bspump.Pipeline()>`.

		definition : dict
				Set of instructions based on which :meth:`processor <bspump.Processor()>` can be constructed.


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
		Returns an ID of a :meth:`processor <bspump.Processor()>` and a :meth:`Pipeline <bspump.Pipeline()>`.

		:return: ID of the :meth:`Pipeline <bspump.Pipeline()>` and self.Id.

		|

		"""
		return "{}.{}".format(self.Pipeline.Id, self.Id)


	def rest_get(self):
		"""
		Description:

		:return:
		"""
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
