import abc

import asyncio

from .processor import ProcessorBase


class Generator(ProcessorBase):
	"""
    Example of use:

.. code:: python

    class MyGenerator(bspump.Generator):

        async def generate(self, context, event, depth):
            for item in event.items:
                await self.Pipeline.inject(context, item, depth + 1)

"""

	def __init__(self, app, pipeline, id=None, config=None):
		super().__init__(app, pipeline, id, config)
		self.PipelineDepth = 0

	def process(self, context, event):
		self.Pipeline.GeneratorFutures.append(
			asyncio.ensure_future(
				self.generate(context, event, self.PipelineDepth),
				loop=self.Loop
			)
		)
		return None

	@abc.abstractmethod
	async def generate(self, context, event, depth):
		raise NotImplemented()
