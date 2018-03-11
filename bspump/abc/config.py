import logging
from asab import Config

#

L = logging.getLogger(__name__)

#

class ConfigObject(object):


	ConfigDefaults = {}


	def __init__(self, config_section_name):
		self.Config = {}
		self.Config.update(self.ConfigDefaults)
		
		if Config.has_section(config_section_name):
			for key, value in Config.items(config_section_name):
				self.Config[key] = value
