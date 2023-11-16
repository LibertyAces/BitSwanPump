from .processor import ProcessorBase


class Generator(ProcessorBase):

	def __init__(self, app, pipeline, id=None, config=None):
		"""
		Description:

		**Parameters**

		app : Application
				Name of the Application.

		pipeline : Pipeline
				Name of the Pipeline.

		id : str, default = None
				ID

		config : JSON, defualt = None
				configuration file containing additional information.

		"""
		super().__init__(app, pipeline, id, config)
		# The correct depth is later set by the pipeline
		self.PipelineDepth = None

	def set_depth(self, depth):
		"""
		Description:

		**Parameters**

		depth : int


		"""
		assert(self.PipelineDepth is None)
		self.PipelineDepth = depth

	def process(self, context, event):
		"""
		Description:

		**Parameters**

		context :

		event : any data type
				information of any data type with timestamp.


		"""
		self.Pipeline.ensure_future(
			self.generate(context, event, self.PipelineDepth + 1)
		)
		return None


	async def generate(self, context, event, depth):
		"""
		Description:

		**Parameters**

		context :

		event : any data type
				information of any data type with timestamp.

		depth : int


		"""
		raise NotImplementedError()
