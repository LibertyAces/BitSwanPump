from .processor import ProcessorBase


class Generator(ProcessorBase):
	"""
	Description:

	:return:
	"""

	def __init__(self, app, pipeline, id=None, config=None):
		"""
		Description:

		:return:
		"""
		super().__init__(app, pipeline, id, config)
		# The correct depth is later set by the pipeline
		self.PipelineDepth = None

	def set_depth(self, depth):
		"""
		Description:

		:return:
		"""
		assert(self.PipelineDepth is None)
		self.PipelineDepth = depth

	def process(self, context, event):
		"""
		Description:

		:return:
		"""
		self.Pipeline.ensure_future(
			self.generate(context, event, self.PipelineDepth + 1)
		)
		return None


	async def generate(self, context, event, depth):
		"""
		Description:

		:return:
		"""
		raise NotImplementedError()
