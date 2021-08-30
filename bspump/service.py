import logging
import asyncio
import asab


L = logging.getLogger(__file__)


class BSPumpService(asab.Service):
	"""
	Service registry based on Service object. Read more in ASAB documentation `Service <https://asab.readthedocs.io/en/latest/asab/service.html`_.

	"""

	def __init__(self, app, service_name="bspump.PumpService"):
		"""
		Initializes parameters passed to the Service class.

		**Parameters**

		app : Application
			Name of the `Application <https://asab.readthedocs.io/en/latest/asab/application.html>`_.

		service_name : str, Service name
			string variable containing ""bspump.PumpService


		|

		"""
		super().__init__(app, service_name)

		self.Pipelines = dict()
		self.Connections = dict()
		self.Lookups = dict()
		self.LookupFactories = []
		self.Matrixes = dict()


	def locate(self, address):
		"""
		locates pipeline, source or processor based on the adressed parameter

		**Parameters**

		address : str, ID
			Address of an pipeline component.

		|

		"""
		if '.' in address:
			p, t = address.split('.', 1)
		else:
			p = address
			t = None
		pipeline = self.Pipelines.get(p)
		if pipeline is None:
			return None
		elif t is None:
			return pipeline

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
		"""
		Adds a pipeline to the BSPump.

		**Parameters**

		pipeline : Pipeline
			Name of the Pipeline.

		"""
		if pipeline.Id in self.Pipelines:
			raise RuntimeError("Pipeline with id '{}' is already registered".format(pipeline.Id))
		self.Pipelines[pipeline.Id] = pipeline

	def add_pipelines(self, *pipelines):
		"""
		Adds a pipelines the BSPump.

		**Parameters**

		*pipelines : list
			List of pipelines that are add to the BSPump.

		|

		"""
		for pipeline in pipelines:
			self.add_pipeline(pipeline)

	def del_pipeline(self, pipeline):
		"""
		Deletes a pipeline from a list of Pipelines.

		**Parameters*

		pipeline : str, ID
			ID of a pipeline.

		|

		"""
		del self.Pipelines[pipeline.Id]

	# Connections

	def add_connection(self, connection):
		"""
		Adds a connection to the Connection dictionary.

		**Parameters**

		connection : str, ID
			ID of a connection.


		:return: connection

		|

		"""
		if connection.Id in self.Connections:
			raise RuntimeError("Connection '{}' already created".format(connection.Id))
		self.Connections[connection.Id] = connection
		return connection

	def add_connections(self, *connections):
		"""
		Adds a connections to the Connection dictionary.

		**Parameters**

		*connection : str, ID
			list of IDs of a connections.

		"""
		for connection in connections:
			self.add_connection(connection)

	def locate_connection(self, connection_id):
		"""
		Locates connection based on connection ID.

		**Parameters**

		connection_id : ID
			Connection ID.


		|

		"""
		from .abc.connection import Connection
		if isinstance(connection_id, Connection):
			return connection_id
		try:
			return self.Connections[connection_id]
		except KeyError:
			raise KeyError(
				"Cannot find connection id '{}' (did you call add_connection() before add_pipeline() ?)".format(connection_id)
			)

	# Lookups

	def add_lookup(self, lookup):
		"""
		Sets a lookup based on Lookup.

		**Parameters**

		lookup : Lookup
			Name of the Lookup.

		:return: lookup

		|

		"""
		if lookup.Id in self.Lookups:
			raise RuntimeError("Lookup '{}' already created".format(lookup.Id))
		self.Lookups[lookup.Id] = lookup
		return lookup

	def add_lookups(self, *lookups):
		"""
		Adds a list of lookups to the Pipeline.

		**Parameters**

		lookup : Lookup
			List of Lookups.


		|

		"""
		for lookup in lookups:
			self.add_lookup(lookup)

	def locate_lookup(self, lookup_id, context=None):
		"""
		Locates lookup based on ID.

		**Parameters**

		lookup_id : ID
			ID of a Lookup.

		context : ,default = None
			Additional information.

		:return: lookup from the lookup service or form the internal dictionary.

		|

		"""
		from .abc.lookup import Lookup
		if isinstance(lookup_id, Lookup):
			return lookup_id

		# TODO: Make sure the lookup is always properly returned
		# #1 - Return lookup from the lookup service
		for lookup_factory in self.LookupFactories:
			lookup = lookup_factory.locate_lookup(lookup_id, context)
			if lookup is not None:
				return lookup

		# #2 - Return lookup from the internal dictionary
		try:
			return self.Lookups[lookup_id]
		except KeyError:
			pass

		raise KeyError("Cannot find lookup id '{}' (did you call add_lookup() ?)".format(lookup_id))

	def add_lookup_factory(self, lookup_factory):
		"""
		Adds a lookup factory

		**Parameters**

		lookup_factory :
			Name of lookup factory.

		|

		"""
		self.LookupFactories.append(lookup_factory)


	# Matrixes

	def add_matrix(self, matrix):
		"""
		Adds a matrix to the Pipeline.

		**Parameters**

		matrix : Matrix
			Name of Matrix.

		:return: matrix

		|

		"""
		if matrix.Id in self.Matrixes:
			raise RuntimeError("Matrix '{}' already created".format(matrix.Id))

		self.Matrixes[matrix.Id] = matrix
		return matrix

	def add_matrixes(self, *matrixes):
		"""
		Adds a list of Matrices to the Pipeline.

		**Parameters**

		*matrixes : list
			List of matrices.

		"""
		for matrix in matrixes:
			self.add_matrix(matrix)

	def locate_matrix(self, matrix_id):
		"""
		Locates a matrix based on matrix ID

		**Parameters**

		matrix_id : str, ID
			ID of a matrix.

		|

		"""
		from .matrix.matrix import Matrix
		if isinstance(matrix_id, Matrix):
			return matrix_id
		try:
			return self.Matrixes[matrix_id]
		except KeyError:
			raise KeyError("Cannot find matrix id '{}' (did you call add_matrix() ?)".format(matrix_id))

	#

	async def initialize(self, app):
		"""
		Initializes an Application based on ASAB `Application <https://asab.readthedocs.io/en/latest/asab/application.html>`_

		**Parameters**

		app : Application
			Name of the `Application <https://asab.readthedocs.io/en/latest/asab/application.html>`_

		"""
		# Run initialization of lookups
		lookup_update_tasks = []
		for lookup in self.Lookups.values():
			if not lookup.Lazy:
				lookup_update_tasks.append(lookup.ensure_future_update(app.Loop))

		# Await all lookups
		if len(lookup_update_tasks) > 0:
			done, pending = await asyncio.wait(lookup_update_tasks, loop=app.Loop)

		# Start all pipelines
		for pipeline in self.Pipelines.values():
			pipeline.start()


	async def finalize(self, app):
		"""
		Stops all the pipelines

		**Parameters**

		app : Application
			Name of the `Application <https://asab.readthedocs.io/en/latest/asab/application.html>`_

		"""
		# Stop all started pipelines
		if len(self.Pipelines) > 0:
			await asyncio.gather(*[pipeline.stop() for pipeline in self.Pipelines.values()], loop=app.Loop)
