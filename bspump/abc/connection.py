import abc
import pprint
from asab import Config

class Connection(abc.ABC):
	
	ConfigDefaults = {}

	def __init__(self, app, connection_id):
		
		self.Config = {}
		self.Config.update(self.ConfigDefaults)
		
		config_section_name = "connection:{}".format(connection_id)
		if Config.has_section(config_section_name):
			for key, value in Config.items(config_section_name):
				self.Config[key] = value
