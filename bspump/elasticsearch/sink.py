import logging
import json
import pprint
import time

import asab
from .. import Sink
#

L = logging.getLogger(__name__)

#

class ElasticSearchSink(Sink):


	ConfigDefaults = {
		"index_prefix" : "bs_",
		"doctype": "doc",
		"version": "18031",
		"time_period": "d",
		"rollover_mechanism": 'time_based',
		"max_index_size": 30*1024*1024*1024, # this is 30GB

	}


	def __init__(self, app, pipeline, connection, id=None, config=None):
		super().__init__(app, pipeline, id=id, config=config)

		self._index = None
		self._index_prefix = self.Config['index_prefix']
		self._doctype = self.Config['doctype']
		self._version = self.Config['version']
		self._rollover_mechanism = self.Config['rollover_mechanism']
		self._max_index_size = int(self.Config['max_index_size'])
		self._time_period = self.parse_index_period(self.Config['time_period'])

		self._connection = pipeline.locate_connection(app, connection)
		
		app.PubSub.subscribe("Application.tick/600!", self._refresh_index)
		self._refresh_index("simulated")
		assert(self._index is not None)


	def process(self, event):
		data = '{{"index": {{ "_index": "{}", "_type": "{}" }}\n{}\n'.format(self._index, self._doctype, json.dumps(event))
		self._connection.consume(data)


	def _refresh_index(self, event_name=None):
		#TODO: implement index update

		if self._rollover_mechanism == 'size':
			self.index_size_based_update()
		elif self._rollover_mechanism == 'time':
			self._refresh_index_time_based()
		elif self._rollover_mechanism == 'fixed':
			self._index = self._index_prefix
		else: 
			print(self._rollover_mechanism)
			#L.error("Invalid rollover mechanism: '{}'. Allowed values are 'index_size_based' or 'time_based'.").format(self._rollover_mechanism)
			raise RuntimeError("Index rollover failed.")


	def _refresh_index_size_based(self):
		url_get_index_size = self._connection.url + '{}*/_stats/store'.format(self._index_prefix)
		stats = self.session.get(url_get_index_size, timeout=self.timeout)
		data = stats.json()

		# if orig_index is not None:
		# 	# Get actual size of the currently active index

		# 	if data.get('_all') is None:
		# 		current_index_size = 0
		# 	else:
		# 		current_index_size = data['_all']['primaries']['store']['size_in_bytes']
		# else:
		# 	current_index_size = 0

		# if (orig_index is None) or (current_index_size >= self.max_index_size):
		# 	# Roll over to a new index
		# 	seqno = int((time.time() - 1500000000) / es_index_period)
		# 	new_es_index = self._generate_es_index(es_type, version, seqno)

		# 	if new_es_index == orig_index:
		# 		L.warning("ElasticSearch index name update resulted in original name, decrease es_index_period value.")

		# 	return new_es_index 		

		# else:
		# 	return orig_index


	def _refresh_index_time_based(self):
		seqno = int((time.time() - 1500000000) / self._time_period)
		self._index = "{}{:05}".format(self._index_prefix, seqno)


	def parse_index_period(self, value):
		if value == 'd': return 60*60*24 # 1 day
		elif value == 'w': return 60*60*24*7 # 7 days
		elif value == 'm': return 60*60*24*28 # 28 days

		return int(value) # Otherwise use value in seconds
