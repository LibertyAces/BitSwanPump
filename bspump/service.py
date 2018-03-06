import asyncio
import asab

class BSPumpService(asab.Service):

	def __init__(self, app):
		super().__init__(app)

		# Set of pipelines
		self.Pipelines = set()


	def add_pipeline(self, pipeline):
		self.Pipelines.add(pipeline)


	async def main(self):
		futures = []
		for pl in self.Pipelines:
			future = asyncio.Future()
			asyncio.ensure_future(pl.process(future))
			futures.append(future)

		await asyncio.wait(futures)

