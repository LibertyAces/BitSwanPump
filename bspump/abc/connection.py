import abc
from .config import ConfigObject

class Connection(abc.ABC, ConfigObject):

	def __init__(self, app, connection_id):
		super().__init__("connection:{}".format(connection_id))
		self.Id = connection_id
