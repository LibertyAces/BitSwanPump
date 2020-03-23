import bspump
import jwt
import logging



###

L = logging.getLogger(__name__)

###


class IntegrityChecker(bspump.Generator):

	# TODO: add description

	ConfigDefaults = {
		'index': 'index-*',
		'key_path': '',
		'algorithm': 'HS256',
		'items_size': 50,
		'scroll_time': 1,
	}

	def __init__(self, app, pipeline, connection, id=None, config=None):
		super().__init__(app, pipeline, id, config)
		self.Connection = pipeline.locate_connection(app, connection)
		self.Index = self.Config['index']
		self.ItemsSize = self.Config['items_size']
		self.Scroll = str(self.Config['scroll_time'])  # Scroll time in minutes

		self.KeyPath = self.Config['key_path']
		self.Algorithm = self.Config['algorithm']
		self.HashSet = {}
		self.Counter = 0

		# Check if the key path is set
		self.JWTPrivateKey = None
		if self.KeyPath == '' or self.KeyPath is None:
			self.JWTPrivateKey = None
		else:
			with open(self.KeyPath, 'r') as file:
				self.JWTPrivateKey = file.read()

		# Locate metricsservice
		metrics_service = app.get_service('asab.MetricsService')
		# Initialize counter
		self.HashCounter = metrics_service.create_counter("hash.counter", tags={}, init_values={'hit': 0, 'miss': 0})


	async def generate(self, context, event, depth):
		# Checking for number of items in index
		url = self.Connection.get_url() + '{}/_count'.format(self.Index)
		async with self.Connection.get_session() as session:
			async with session.get(
				url,
				json={
					'query': {
						'bool': {
							'must': {
								'match_all': {}
							}
						}
					}},
				headers={'Content-Type': 'application/json'}
			) as response:
				if response.status != 200:
					data = await response.text()
					L.error("Failed to fetch data from ElasticSearch: {} from {}\n{}".format(response.status, url, data))
					return

				msg = await response.json()

		count = msg['count']
		if count > 0:
			# Getting data from ES
			while True:
				path = '{}/_search?scroll={}m'.format(self.Index, self.Scroll)
				url = self.Connection.get_url() + path
				async with self.Connection.get_session() as session:
					async with session.post(
						url,
						json={
							"size": self.ItemsSize,
							'query': {
								'bool': {
									'must': {
										'match_all': {}
									}
								}
							}},
						headers={'Content-Type': 'application/json'}
					) as response:

						if response.status != 200:
							data = await response.text()
							L.error("Failed to fetch data from ElasticSearch: {} from {}\n{}".format(response.status, url, data))
							break

						msg = await response.json()

				hits = msg['hits']['hits']
				if len(hits) == 0:
					break

				# Decoding finalhashes by object
				if self.JWTPrivateKey is not None:
					for JSONobject in hits:
						self.object_check(JSONobject)
		else:
			L.warning('No data in ElasticSearch.')

	# Checking for hash
	def object_check(self, JSONobject):
		if 'hash' in JSONobject:
			decode = jwt.decode(JSONobject["hash"], self.JWTPrivateKey, algorithm=self.Algorithm)
			self.compare(JSONobject, decode)
		else:
			for key in JSONobject:
				if type(JSONobject[key]) is dict:
					self.object_check(JSONobject[key])

	# Compare data
	def compare(self, original_data, decoded_data):
		# Removing hash from the decoded data if there is any
		previous_hash = decoded_data.pop("hash", None)
		# And appending it with recent hash to the HashSet dictionary
		if 'hash' in original_data:
			self.Counter += 1
			self.HashSet.update({str(self.Counter): {"hash": original_data["hash"], "prev_hash": previous_hash}})

		for key in original_data:
			# Avoiding comparison on hash key to prevent incomparability
			if str(key) != 'hash':
				# Recursive iteration through nested dictionaries
				if type(original_data[key]) is dict:
					self.compare(original_data[key], decoded_data[key])
				else:
					if original_data[key] == decoded_data[key]:
						self.HashCounter.add('hit', 1)
						L.info('Integrity has been approved.')
					else:
						self.HashCounter.add('miss', 1)
						L.warning('Integrity has not been enthroned!')

		# TODO: return self.HashSet ?
