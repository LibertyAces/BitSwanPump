from ..abc.lookup import Lookup
import pymemcache.client
import logging

L = logging.getLogger(__name__)

###


class MemcachedLookup(Lookup):

	ConfigDefaults = {
		'max_size': 1000,
		'expiry_seconds': 3600,
		'server': '127.0.0.1:11211',
	}


	def __init__(self, app, id=None, config=None):
		super().__init__(app, id=id, config=config)

		self.App = app
		self.MaxSize = self.Config['max_size']
		self.Expiration = self.Config['expiry_seconds']
		self.Server = self.Config['server']
		self.Target = None

		if len(self.Server) > 0:
			self.Client = pymemcache.client.base.Client(tuple(self.Server.split(":")))
		else:
			raise Exception("Memcache service path not set.")


	def set(self, to_chache: dict):
		for key, value in to_chache.items():
			returned = self.Client.set(key, value, expire=self.Expiration)
		if returned is not True:
			L.warning("Setting a memcached key-value failed")
		L.debug("Successfully set key-value")

	def get(self, key):
		return self.Client.get(key)

	def delete(self, key):
		self.Client.delete(key)
		L.debug("Deleted {} form memcache.".format(key))


	def close_connection(self):
		self.Client.close()
		L.info("Closed connection to memcache")


	def flush_all(self):
		self.Client.flush_all()
		L.info("Chache flushed")
