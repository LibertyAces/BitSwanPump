import logging
import asyncio
import asab

from .abc.connection import Connection

#

L = logging.getLogger(__file__)

#

class BSPumpService(asab.Service):

	def __init__(self, app):
		super().__init__(app)

		self.Pipelines = dict()
		self.Connections = dict()


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

	async def main(self):
		# Start all pipelines
		if len(self.Pipelines) > 0:
			futures = []
			for p in self.Pipelines.values():
				f = asyncio.ensure_future(p.start())
				futures.append(f)

			s, f = await asyncio.wait(futures, return_when=asyncio.FIRST_EXCEPTION)
			if len(f) == 0:
				L.info("{} pipeline(s) started".format(len(s)))
			else:
				L.error("{} pipeline(s) started, {} failed to start!".format(len(s), len(f)))
