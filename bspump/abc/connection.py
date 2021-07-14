import abc
from asab import ConfigObject


class Connection(abc.ABC, ConfigObject):
	"""
	Description: Connection class is responsible for creating a connection between items or services within the infrastructure of BSPump.
	Their main use is to create connection with the main components of BSPump: source, processor and sink.

	|

	"""

	def __init__(self, app, id=None, config=None):
		"""
		Description:

		|

		"""

		_id = id if id is not None else self.__class__.__name__
		super().__init__("connection:{}".format(_id), config=config)

		self.App = app
		self.Loop = app.Loop

		self.Id = _id


	def time(self):
		"""
		Description:

		:return: time

		|

		"""
		return self.App.time()


	@classmethod
	def construct(cls, app, definition: dict):
		"""
		Description:

		:return: cls

		|

		"""
		newid = definition.get('id')
		config = definition.get('config')
		return cls(app, newid, config)
