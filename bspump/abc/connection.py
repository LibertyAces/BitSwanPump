import abc
from asab import ConfigObject


class Connection(abc.ABC, ConfigObject):

	def __init__(self, app, connection_id, config=None):
		super().__init__("connection:{}".format(connection_id), config=config)
		self.Id = connection_id

	@classmethod
	def construct(cls, app, definition:dict):
		newid = definition.get('id')
		config = definition.get('config')
		return cls(app, newid, config)
