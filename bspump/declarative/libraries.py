import abc
import os

import aiozk


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
