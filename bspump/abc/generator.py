from .processor import ProcessorBase


class Generator(ProcessorBase):

	def __init__(self, app, pipeline, id=None, config=None):
		super().__init__(app, pipeline, id, config)
		# The correct depth is later set by the pipeline
		self.PipelineDepth = None

	def set_depth(self, depth):
		assert(self.PipelineDepth is None)
		self.PipelineDepth = depth

	def process(self, context, event):
		self.Pipeline.ensure_future(
			self.generate(context, event, self.PipelineDepth + 1)
		)
		return None


	async def generate(self, context, event, depth):
		raise NotImplementedError()
