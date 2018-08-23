import logging

from ..abc.connection import Connection

#

L = logging.getLogger(__name__)

#


class KafkaConnection(Connection):

	ConfigDefaults = {
		'bootstrap_servers': 'localhost:9092',
	}

	def get_bootstrap_servers(self):
		return self.Config['bootstrap_servers']
