import logging

import motor.motor_asyncio
import pymongo

from ..abc.connection import Connection

#

L = logging.getLogger(__name__)

#


# TODO: Generalize this function to ConfigObject
def _get_int_or_none(config_obj, key):
	v = config_obj.get(key)
	if isinstance(v, str) and len(v) == 0:
		return None
	try:
		return int(v)
	except ValueError:
		L.error("Expects integer value", struct_data={'key': key, 'value': v})
		return None


# TODO: Generalize this function to ConfigObject
def _get_str_or_none(config_obj, key):
	v = config_obj.get(key)
	if len(v) == 0:
		return None
	return v


class MongoDBConnection(Connection):

	'''
Examples of configurations:

[connection:Mongo]
host=localhost
port=27017


[connection:Mongo]
host=mongodb://localhost:27017

[connection:Mongo]
host=mongodb://host1,host2/?replicaSet=my-replicaset-name


	'''

	ConfigDefaults = {
		'host': 'localhost',  # hostname or IP address or Unix domain socket path of a single mongod or mongos instance to connect to, or a mongodb URI, or a list of hostnames / mongodb URIs.
		'port': 27017,
		'username': '',
		'password': '',
		'max_pool_size': 100,
		'min_pool_size': 0,
		'max_idle_time': '',
		'socket_timeout': '',
		'connect_timeout': '',
		'server_selection_timeout': '',
		'wait_queue_timeout': '',
		'wait_queue_multiple': '',
		'heartbeat_frequency': 10 * 1000,  # 10 seconds
		'database': 'database',
	}

	def __init__(self, app, id=None, config=None):
		super().__init__(app, id=id, config=config)

		# TODO: SSL ...

		self.Client = motor.motor_asyncio.AsyncIOMotorClient(
			host=self.Config['host'],
			port=_get_int_or_none(self.Config, 'port'),
			username=_get_str_or_none(self.Config, 'username'),
			password=_get_str_or_none(self.Config, 'password'),
			maxPoolSize=_get_int_or_none(self.Config, 'max_pool_size'),
			minPoolSize=_get_int_or_none(self.Config, 'min_pool_size'),
			maxIdleTimeMS=_get_int_or_none(self.Config, 'max_idle_time'),
			socketTimeoutMS=_get_int_or_none(self.Config, 'socket_timeout'),
			connectTimeoutMS=_get_int_or_none(self.Config, 'connect_timeout'),
			waitQueueTimeoutMS=_get_int_or_none(self.Config, 'wait_queue_timeout'),
			waitQueueMultiple=_get_int_or_none(self.Config, 'wait_queue_multiple'),
			heartbeatFrequencyMS=_get_int_or_none(self.Config, 'heartbeat_frequency'),
			appname=id,
			driver=pymongo.driver_info.DriverInfo(
				name="bspump.MongoDBConnection",
				# TODO: version=...
				platform="BitSwan",
			),
			io_loop=app.Loop
		)

		self.Database = self.Config['database']
