import abc
import os

import aiozk
import pymongo


class DeclarationLibrary(abc.ABC):

	@abc.abstractmethod
	def read(self, identifier):
		"""
		:param identifier: identifier of the declaration
		:return: loaded declaration or None, if no declaration identified by the identifier found
		"""
		pass


class FileDeclarationLibrary(DeclarationLibrary):

	def __init__(self, basedir='.'):
		super().__init__()
		self.BaseDir = basedir

	def read(self, identifier):
		# Try to load YAML from a disk
		fname = os.path.join(self.BaseDir, identifier + '.yaml')
		if os.path.exists(fname):
			with open(fname, 'r') as f:
				return f.read()
		return None


class ZooKeeperDeclarationLibrary(DeclarationLibrary):
	"""
	Expects a ZooKeeperClient.
	"""

	def __init__(self, zookeeper_client, zookeeper_path, encoding="utf-8"):
		super().__init__()
		self.ZooKeeperClient = zookeeper_client
		self.ZooKeeperPath = zookeeper_path
		self.Encoding = encoding
		self.ZookeeperData = {}

	async def load(self):
		try:
			for document in await self.ZooKeeperClient.get_children(self.ZooKeeperPath):
				self.ZookeeperData[document] = await self.ZooKeeperClient.get_data(
					"{}/{}".format(self.ZooKeeperPath, document)
				)
		except aiozk.exc.NoNode:
			pass

	def read(self, identifier):
		for key, declaration in self.ZookeeperData.items():
			if key == identifier + '.yaml':
				if isinstance(declaration, bytes):
					declaration = declaration.decode(self.Encoding)
				return declaration
		return None


class MongoDeclarationLibrary(DeclarationLibrary):

	def __init__(self, mongodb_host="", mongodb_database="", mongodb_collection="", key_element="identifier", data_element="data", _filter=None):
		"""
		:param mongodb_host: specify MongoDB hostname in format: mongodb://mongodb1:27017
		:param mongodb_database: specify MongoDB database
		:param mongodb_collection: specify collection (like lookups, parsers etc.)
		:param key_element: specify the key element to load the declarations by
		:param data_element: specify the element where the declaration is used inside the MongoDB document
		:param _filter: specify additional MongoDB filter if needed, f. e. by type or folder
		"""
		super().__init__()
		self.MongoDBHost = mongodb_host
		self.MongoDBDatabase = mongodb_database
		self.MongoDBCollection = mongodb_collection
		self.KeyElement = key_element
		self.DataElement = data_element
		self.MongoDBClient = pymongo.MongoClient(self.MongoDBHost)

		if _filter is None:
			self.Filter = {}
		else:
			self.Filter = _filter

	def read(self, identifier):
		_filter = {self.KeyElement: identifier}
		_filter.update(self.Filter)
		declaration_yml = self.MongoDBClient[self.MongoDBDatabase][self.MongoDBCollection].find_one(_filter)
		if declaration_yml is not None:
			return declaration_yml[self.DataElement]
		return None

	def list(self):
		"""
		List all available declarations.
		:return: declarations
		"""
		declarations = self.MongoDBClient[self.MongoDBDatabase][self.MongoDBCollection].find(self.Filter)
		for declaration_yml in declarations:
			yield declaration_yml
