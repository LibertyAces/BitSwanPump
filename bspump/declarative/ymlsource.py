import abc
import os
import pymongo


class YMLSource(abc.ABC):

	@abc.abstractmethod
	def read(self, identifier):
		"""
		:param identifier: identifier of the declaration
		:return: loaded declaration or None, if no declaration identified by the identifier found
		"""
		pass


class FileYMLSource(YMLSource):

	def __init__(self, basedir='.'):
		super().__init__()
		self.BaseDir = basedir

	def read(self, identifier):
		# Try to load YAML from a disk
		fname = os.path.join(self.BaseDir, identifier + '.yml')
		if os.path.exists(fname):
			with open(fname, 'r') as f:
				return f.read()
		return None


class MongoDBYMLSource(YMLSource):

	def __init__(self, mongodb_host="", mongodb_database="", mongodb_collection="", key_element="_id", data_element="data"):
		super().__init__()
		self.MongoDBHost = mongodb_host
		self.MongoDBDatabase = mongodb_database
		self.MongoDBCollection = mongodb_collection
		self.KeyElement = key_element
		self.DataElement = data_element
		self.MongoDBClient = pymongo.MongoClient(self.MongoDBHost)

	def read(self, identifier):
		declaration_yml = self.MongoDBClient[self.MongoDBDatabase][self.MongoDBCollection].find_one(
			{
				self.KeyElement: identifier
			}
		)
		if declaration_yml is not None:
			return declaration_yml[self.DataElement]
		return None

	def list(self):
		"""
		List all available declarations.
		:return: declarations
		"""
		for declaration_yml in self.MongoDBClient[self.MongoDBDatabase][self.MongoDBCollection].find({}):
			yield declaration_yml
