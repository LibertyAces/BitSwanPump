import logging
import json
import asyncio
import time
import requests

import asab
from .. import Sink

#

L = logging.getLogger(__name__)

#

class ElasticSearchSink(Sink):


	ConfigDefaults = {
		"index_prefix" : "bspump_",
		"doctype": "doc",
		"time_period": "d",
		"rollover_mechanism": 'time',
		"max_index_size": 30*1024*1024*1024, #This is 30GB
		"timeout": 30

	}


	def __init__(self, app, pipeline, connection, id=None, config=None):
		super().__init__(app, pipeline, id=id, config=config)

		self._index = None
		self._index_prefix = self.Config['index_prefix']
		self._doctype = self.Config['doctype']
		self._rollover_mechanism = self.Config['rollover_mechanism']
		self._max_index_size = int(self.Config['max_index_size'])
		self._time_period = self.parse_index_period(self.Config['time_period'])
		self.timeout = self.Config['timeout']

		self._connection = pipeline.locate_connection(app, connection)
		
		app.PubSub.subscribe("Application.tick/600!", self._refresh_index)
		app.PubSub.subscribe("ElasticSearchConnection.unpause!", self._connection_unpause)
		self._refresh_index("simulated")
		assert(self._index is not None)


	def process(self, event):
		data = '{{"index": {{ "_index": "{}", "_type": "{}" }}\n{}\n'.format(self._index, self._doctype, json.dumps(event))
		
		ret = self._connection.consume(data)
		if ret == False:
			self.Pipeline.throttle(self, True)


	def _connection_unpause(self, event_name, connection):
		if connection != self._connection:
			return

		self.Pipeline.throttle(self, False)


	def _refresh_index(self, event_name=None):
		if self._rollover_mechanism == 'size':
			self._refresh_index_size_based()
		elif self._rollover_mechanism == 'time':
			self._refresh_index_time_based()
		elif self._rollover_mechanism == 'fixed':
			self._index = self._index_prefix
		else: 
			L.error("Invalid rollover mechanism:. Allowed values are 'size', 'time' and 'fixed'.")
			raise RuntimeError("Index rollover failed.")


	def _refresh_index_size_based(self):
		url_get_index_size = self._connection.url + '{}*/_stats/store'.format(self._index_prefix)

		with requests.Session() as session:
			response = session.get(url_get_index_size, timeout=self.timeout)

		if response.status_code != 200:
			L.error("Failed to get indices' statistics from ElasticSearch.")

		data = response.json()

		if data["_shards"]["failed"] != 0:
			L.warning("There was one or more failed shards in the query.")

		# Create a list of indices and sort them 
		ls = []
		for index_name, index_stats in data['indices'].items():
			ls.append(index_name)

		sorted_ls = sorted(ls, key=lambda item: item.rsplit('_', 1)[-1], reverse=True)

		if len(sorted_ls) > 0:
			if (data['indices'][sorted_ls[0]]['primaries']['store']['size_in_bytes'] > self._max_index_size)  and (self._index is not None):
				_ , split_index = self._index.rsplit('_',1)
				split_index =int(split_index) + 1
				self._index = self._index_prefix + '{:05}'.format(split_index[1])

		if self._index is None:
			self._index = self._index_prefix + '{:05}'.format(1)

	def _refresh_index_time_based(self):
		seqno = int((time.time() - 1500000000) / self._time_period)
		self._index = "{}{:05}".format(self._index_prefix, seqno)


	def parse_index_period(self, value):
		if value == 'd': return 60*60*24 # 1 day
		elif value == 'w': return 60*60*24*7 # 7 days
		elif value == 'm': return 60*60*24*28 # 28 days

		return int(value) # Otherwise use value in seconds
