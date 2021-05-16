from pymemcache.client import base
import subprocess
import logging

L = logging.getLogger(__name__)


class Memcached:
	"""
	Memcached for use in bspump.
	Parameters:
		memcache - ip:port of memcache service
	"""
	def __init__(self, app, max_size=1000, expiry_seconds=0, memcache=None *args, **kwargs):
		super().__init__(*args, **kwargs)
		# TODO: Configurable via configfile?
		if memcache:
			self.Client = base.Client(tuple(memcache.split(":")))
		else:
			L.error("Memcache service path not set.")

		self.App = app
		self.MaxSize = max_size
		self.Expiration = expiry_seconds


	def set(self, to_chache: dict):
		for key, value in to_chache:
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
