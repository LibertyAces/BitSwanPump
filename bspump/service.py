import logging
import asyncio
import asab

#

L = logging.getLogger(__file__)

#

class BSPumpService(asab.Service):

	def __init__(self, app):
		super().__init__(app)

		# Set of pipelines
		self.Pipelines = set()


	def add_pipeline(self, pipeline):
		self.Pipelines.add(pipeline)


	async def main(self):
		# Start all pipelines
		if len(self.Pipelines) > 0:
			futures = []
			for p in self.Pipelines:
				f = asyncio.ensure_future(p.start())
				futures.append(f)

			s, f = await asyncio.wait(futures, return_when=asyncio.FIRST_EXCEPTION)
			if len(f) == 0:
				L.info("{} pipeline(s) started".format(len(s)))
			else:
				L.error("{} pipeline(s) started, {} failed to start!".format(len(s), len(f)))
