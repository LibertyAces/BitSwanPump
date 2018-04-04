import logging
import asyncio
import asab

from .abc.connection import Connection

#

L = logging.getLogger(__file__)

#

class BSPumpService(asab.Service):

	def __init__(self, app, service_name="bspump.PumpService"):
		super().__init__(app, service_name)

		self.Pipelines = dict()
		self.Connections = dict()


	def locate(self, address):
		p, t = address.split('.', 1)
		pipeline = self.Pipelines.get(p)
		if pipeline is None:
			return None

		if t[:1] == '*':
			for source in pipeline.Sources:
				if source.Id == t[1:]:
					return source
		else:
			for processor in pipeline.iter_processors():
				if processor.Id == t:
					return processor

		return None


	# Pipelines

	def add_pipeline(self, pipeline):
		if pipeline.Id in self.Pipelines:
			raise RuntimeError("Pipeline with id '{}' is already registered".format(pipeline.Id))
		self.Pipelines[pipeline.Id] = pipeline

	def add_pipelines(self, *pipelines):
		for pipeline in pipelines:
			self.add_pipeline(pipeline)


	# Connections

	def add_connection(self, connection):
		self.Connections[connection.Id] = connection

	def add_connections(self, *connections):
		for connection in connections:
			self.add_connection(connection)

	def locate_connection(self, connection_id):
		if isinstance(connection_id, Connection): return connection_id
		try:
			return self.Connections[connection_id]
		except KeyError:
			raise KeyError("Cannot find connection id '{}'".format(connection_id))


	#

	def start(self):
		# Start all pipelines
		for pipeline in self.Pipelines.values():
			pipeline.start()


	async def finalize(self, app):
		# Stop all started pipelines
		if len(self.Pipelines) > 0:
			await asyncio.gather(*[pipeline.stop() for pipeline in self.Pipelines.values()], loop=app.Loop)
