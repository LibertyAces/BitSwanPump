import abc
import logging
import json

import asab

###

L = logging.getLogger(__name__)

###


class Model(abc.ABC, asab.ConfigObject):
	'''
		Generic `Model` object. Loads trained model and parameters.

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
		'''
		Load model from file.
		'''
		pass


	def load_parameters_from_file(self):
		'''
		Loads model parameters from json file. Override if needed.
		'''
		with open(self.PathParameters) as f:
			self.Parameters = json.load(f)


	async def update(self):
		'''
		Updates model on fly.
		'''
		pass

	@abc.abstractmethod
	def transform(self, *args):
		'''
		Method used to transform data for model input.
		'''
		raise NotImplementedError()


	@abc.abstractmethod
	def predict(self, *args):
		'''
		Method uses model to predict value from sample.
		'''
		raise NotImplementedError()
