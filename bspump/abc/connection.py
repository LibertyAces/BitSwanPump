import abc
from asab import ConfigObject


class Connection(abc.ABC, ConfigObject):

	def __init__(self, app, id=None, config=None):
		_id = id if id is not None else self.__class__.__name__
		super().__init__("connection:{}".format(_id), config=config)

		self.App = app
		self.Loop = app.Loop

		self.Id = _id


	def time(self):
		return self.App.time()


	@classmethod
	def construct(cls, app, definition: dict):
		newid = definition.get('id')
		config = definition.get('config')
		return cls(app, newid, config)
