import abc
from .config import ConfigObject

class Connection(abc.ABC, ConfigObject):

	def __init__(self, app, connection_id, config=None):
		super().__init__("connection:{}".format(connection_id), config=None)
		self.Id = connection_id
