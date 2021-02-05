import abc
import os
import glob

import aiozk
import logging

#

L = logging.getLogger(__name__)

#


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

		recursive = basedir.endswith("*")
		if not recursive:
			self.BaseDir = os.path.join(self.BaseDir, "*")
		else:
			self.BaseDir = os.path.join(os.path.join(self.BaseDir[:-2], "**"), "*")

		file_names = glob.iglob(self.BaseDir, recursive=recursive)
		self.FileNames = [ file_name for file_name in file_names ]

	def read(self, identifier):

		# Try to load YAML from a disk
		for file_name in self.FileNames:

			if file_name.endswith(identifier + '.yaml') or file_name.endswith(identifier + '.yml'):

				with open(file_name, 'r') as f:
					return f.read()

		return None


class ZooKeeperDeclarationLibrary(DeclarationLibrary):
	"""
	Expects a ZooKeeperClient.
	"""

	def __init__(self, zookeeper_client, zookeeper_path, encoding="utf-8"):
		super().__init__()
		self.ZooKeeperClient = zookeeper_client

		self.ZooKeeperPath = zookeeper_path.replace("/**", "")
		self.Recursive = zookeeper_path.endswith("*")

		if self.Recursive:
			self.ZooKeeperPath = self.ZooKeeperPath[:-2]

		self.Encoding = encoding
		self.ZookeeperData = {}

	async def load(self):
		await self._load_by_path(self.ZooKeeperPath)

	async def _load_by_path(self, zookeeper_path):
		try:

			for document in await self.ZooKeeperClient.get_children(zookeeper_path):

				try:

					document_zookeeper_path = "{}/{}".format(zookeeper_path, document)

					if self.Recursive:
						await self._load_by_path(document_zookeeper_path)

					try:
						self.ZookeeperData[document] = await self.ZooKeeperClient.get_data(
							document_zookeeper_path
						)
					except (aiozk.exc.NoNode, IndexError):
						pass

				except Exception as e:
					L.warning("Exception occurred during ZooKeeper load: '{}'".format(e))

		except aiozk.exc.NoNode:
			pass

	def read(self, identifier):
		for key, declaration in self.ZookeeperData.items():
			if key == identifier + '.yaml':
				if isinstance(declaration, bytes):
					declaration = declaration.decode(self.Encoding)
				return declaration
		return None
