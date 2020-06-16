import abc
import logging
import json

import asab

###

L = logging.getLogger(__name__)

###


class Model(abc.ABC, asab.ConfigObject):
	'''
		Generic `Model` object. 

	'''

	ConfigDefaults = {
		'path_model': '',  # path to serialized model
		'path_parameters': '',  # path to serialized model
	}


	def __init__(self, app, id=None, config=None):
		self.Id = id if id is not None else self.__class__.__name__
		super().__init__("model:{}".format(self.Id), config=config)
		self.PathModel = self.Config['path_model']
		self.PathParameters = self.Config['path_parameters']
		self.App = app
		self.Loop = app.Loop


	@abc.abstractmethod
	def load_model_from_file(self):
		pass


	def load_parameters_from_file(self):
		with open(self.PathParameters) as f:
			self.Parameters = json.load(f)


	async def update(self):
		pass

	@abc.abstractmethod
	def transform(self, *args):
		raise NotImplementedError()


	@abc.abstractmethod
	def predict(self, *args):
		raise NotImplementedError()
