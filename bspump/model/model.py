import abc
import logging

import asab

###

L = logging.getLogger(__name__)

###


class Model(abc.ABC, asab.ConfigObject):
	'''
		Generic `Model` object.

	'''

	ConfigDefaults = {
		'path': '', # path to serialized model
	}


	def __init__(self, app, id=None, config=None):
		self.Id = id if id is not None else self.__class__.__name__
		super().__init__("model:{}".format(self.Id), config=config)

		self.App = app
		self.Loop = app.Loop


	@abc.abstractmethod
	def load_from_file(self):
		pass


	async def update(self):
		pass

	@abc.abstractmethod
	def transform(self, data):
		raise NotImplementedError()


	@abc.abstractmethod
	def predict(self, data):
		raise NotImplementedError()
