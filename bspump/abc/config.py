import inspect
from asab import Config


class ConfigObject(object):


	ConfigDefaults = {}


	def __init__(self, config_section_name, config=None):
		self.Config = {}

		for base_class in inspect.getmro(self.__class__):
			if not hasattr(base_class, 'ConfigDefaults'): continue
			if len(base_class.ConfigDefaults) == 0: continue
			self.Config.update(base_class.ConfigDefaults)

		if config is not None:
			self.Config.update(config)
		
		if Config.has_section(config_section_name):
			for key, value in Config.items(config_section_name):
				self.Config[key] = value
