import asyncio
import logging
import random
import ssl
import aiohttp
import urllib.parse

import asab

from ..abc.connection import Connection
from asab.tls import SSLContextBuilder

#

L = logging.getLogger(__name__)

#


class ElasticSearchBulk(object):

	def __init__(self, connection, index, max_size):
		"""
		Initializes the variables

		**Parameters**

		connection : Connection
				Name of the Connection.

		index : str
				???

		max_size : int
				Maximal size of bulks.

		"""
		self.Index = index
		self.Aging = 0
		self.Capacity = max_size
		self.Items = []
		self.InsertMetric = connection.InsertMetric
		self.FailLogMaxSize = connection.FailLogMaxSize
		self.LogFailedDocuments = connection.LogFailedDocuments
		self.FilterPath = connection.FilterPath
		self.CreatedAt = connection.App.time()
		self.ESResponseCodes = connection.ESResponseCodes


	def consume(self, data_feeder_generator):
		"""
		Appends all items in data_feeder_generator to Items list. Consumer also resets Aging and Capacity.

		**Parameters**

		data_feeder_generator : list
				list of our data that will be passed to a generator and later Uploaded to ElasticSearch.

		:return: self.Capacity <= 0

		"""
		for item in data_feeder_generator:
			self.Items.append(item)
			self.Capacity -= len(item)

		# Reset the aging so the bulk can be filled up to its capacity
		self.Aging = 0

		# Was the capacity of the bulk exceeded?
		return self.Capacity <= 0


	async def _get_data_from_items(self):
		for item in self.Items:
			yield item


	async def upload(self, url, session, ssl_context, timeout):
		"""
		Uploads data to Elastic Search.

		**Parameters**

		url : string
				Uses URL from config to connect to ElasticSearch Rest API.

		session : ?
				?

		timeout : int
				uses timout value from config. Value of time for how long we want to be connected to ElasticSearch.

		:return: ?

		|

		"""
		items_count = len(self.Items)
		if items_count == 0:
			return

		url = url + '{}/_bulk?filter_path={}'.format(self.Index, self.FilterPath)

		try:
			resp = await session.post(
				url,
				data=self._get_data_from_items(),
				ssl=ssl_context,
				timeout=timeout,
			)
		except OSError as e:
			# This means that there was a hard error such as network or DNS failure
			# Likely no communication took place with ElasticSearch
			L.warning(
				"Encountered OS Error",
				struct_data={"reason": e},
			)

			return False

		# Obtain the response from ElasticSearch, which should always be a json
		try:
			resp_body = await resp.json()
		except Exception as e:
			# We received something else than JSON, that's bad
			# Let's assume that the bulk did not reach ElasticSearch
			L.warning(
				"Unknown exception",
				struct_data={"reason": e},
			)
			return False

		if resp.status == 200:

			# Check that all documents were successfully inserted to ElasticSearch
			# If there are no error messages, we are done here
			if not resp_body.get("errors", False):
				self.InsertMetric.add("ok", items_count)
				return True

			# Some of the documents were not inserted properly,
			# usually because of attributes mismatch, see:
			# https://www.elastic.co/guide/en/elasticsearch/reference/current/docs-bulk.html

			response_items = resp_body.get("items")
			self.partial_error_callback(response_items)

			# When the log handling is not precise,
			# the iteration only happens on error items natively
			# Log first 20 errors
			counter = 0
			for response_item in response_items:
				if "error" not in response_item.get("index", ""):
					continue

				if self.LogFailedDocuments and counter < self.FailLogMaxSize:
					L.error(
						"Failed to insert document into Elasticsearch: '{}'".format(response_item),
						struct_data={
							"status": resp.status,
							"reason": self.ESResponseCodes.get(resp.status, resp.status),
						},
					)


				counter += 1

			# Show remaining log messages
			if self.LogFailedDocuments and counter > self.FailLogMaxSize:
				L.error(
					"Failed to insert document into Elasticsearch. Failed insertions",
					struct_data={
						"count": counter - self.FailLogMaxSize,
					}
				)

			# Insert metrics
			self.InsertMetric.add("fail", counter)
			self.InsertMetric.add("ok", items_count - counter)

		else:

			# The major Elasticsearch error occurred while inserting documents, response was not 200
			self.InsertMetric.add("fail", items_count)
			L.error(
				"Failed to insert document into Elasticsearch: '{}'".format(resp_body),
				struct_data={
					"status": resp.status,
					"reason": self.ESResponseCodes.get(resp.status, resp.status),
				},
			)

			return self.full_error_callback(self.Items, resp.status)

		return True


	def partial_error_callback(self, response_items):
		"""
		Description: When an upload to Elasticsearch fails for error items (document could not be inserted),
		this callback is called.

		**Parameters**

		response_items :

		:param response_items: list with dict items: {"index": {"_id": ..., "error": ...}}

		:return:
		"""
		L.error(
			"Failed to insert items in the elasticsearch",
			struct_data={
				"items": response_items[:10],
			}
		)


	def full_error_callback(self, bulk_items, return_code):
		"""
		Description: When an upload to Elasticsearch fails b/c of Elasticsearch error,
		this callback is called.

		**Parameters**

		bulk_items : list
				list with tuple items: (_id, data)

		return_code :
				Elasticsearch return code

		:return: False if the bulk is to be resumbitted again

		|

		"""
		return True


class ElasticSearchConnection(Connection):
	"""
	Description:

	**Sample Config**

	url : ''http'://{ip/localhost}:{port}'
			URL of the source. Could be multi-URL. Each URL should be separated by ';' to a node in Elasticsearch cluster.

	username : 'string' , default = ' '
			Used when authentication is required

	password : 'string', default = ' '
			Used when authentication is required

	api_key : 'string', default = ' '
			Used when authentication is required (instead of username and password)

	cafile : 'string', default = ' '
			Used for authentication when ssl layer is required

	loader_per_url : int, default = 4
			Number of parallel loaders per URL.

	output_queue_max_size : int, default = 10
			Maximum queue size.

	bulk_out_max_size : ? * ? * ?, default = 12 * 1024 * 1024
			??

	timeout : int, default = 300
			Timout value.

	fail_log_max_size : int, default =  20
			Maximum size of failed log messages.

	precise_error_handling : bool, default = False
			If True all Errors will be logged, If false soft errors will be omitted in the Logs.



	"""

	ConfigDefaults = {
		'url': '',
		# Could be multi-URL. Each URL should be separated by ';' to a node in Elasticsearch cluster
		'username': '',
		'password': '',
		'api_key': '',
		'loader_per_url': 4,  # Number of parallel loaders per URL
		'output_queue_max_size': 10,
		'bulk_out_max_size': 12 * 1024 * 1024,
		'timeout': 300,
		'fail_log_max_size': 20,
		'precise_error_handling': False,
		'log_failed_documents': True,
		'bulk_lifespan': 30,  # Lifespan is the maximum time for bulk existence, per tick/second
		'max_bulk_age': 2,  # Age is when no event comes to the bulk, per tick/second
	}

	def __init__(self, app, id=None, config=None):
		"""
		Description:

		**Parameters**

		app : Application
				Name of the Application

		id : ID, default= None
				ID

		config : JSON or dict, default= None
				configuration file with additional information for the methods.

		"""
		super().__init__(app, id=id, config=config)

		self._output_queue_max_size = int(self.Config['output_queue_max_size'])
		self._output_queue = asyncio.Queue()

		url = self.Config["url"]

		if len(url) == 0:
			url = asab.Config.getmultiline('elasticsearch', 'url', fallback='')
			url_hot = asab.Config.getmultiline('elasticsearch', 'url_hot', fallback=url)

		else:
			url_hot = [url]

		self.NodeUrls = get_url_list(url_hot)

		if len(self.NodeUrls) == 0:
			raise RuntimeError("No ElasticSearch URL has been provided.")

		# Authorization: username or API-key
		username = self.Config.get('username')
		if len(username) == 0:
			username = asab.Config.get('elasticsearch', 'username', fallback='')

		password = self.Config.get('password')
		if len(password) == 0:
			password = asab.Config.get('elasticsearch', 'password', fallback='')

		api_key = self.Config.get('api_key')
		if len(api_key) == 0:
			api_key = asab.Config.get('elasticsearch', 'api_key', fallback='')

		# The lifespan of bulks (per second)
		self.BulkLifespan = self.Config.getint('bulk_lifespan')

		# Maximum age of bulks (per second)
		self.MaxBulkAge = self.Config.getint('max_bulk_age')

		# Build headers
		self.Headers = build_headers(username, password, api_key)

		# Build ssl context
		if self.NodeUrls[0].startswith('https://'):
			if asab.Config.has_section('connection:{}'.format(id)) and section_has_ssl_option('connection:{}'.format(id)):
				# use the old section if it has data for SSL or default to the [elasticsearch] section
				self.SSLContextBuilder = SSLContextBuilder(config_section_name='connection:{}'.format(id))
			else:
				self.SSLContextBuilder = SSLContextBuilder(config_section_name='elasticsearch')
			self.SSLContext = self.SSLContextBuilder.build(ssl.PROTOCOL_TLS_CLIENT)
		else:
			self.SSLContext = None

		# These parameters can be specified only in [connection:XXXXX] config section
		self._loader_per_url = int(self.Config['loader_per_url'])

		self._bulk_out_max_size = int(self.Config['bulk_out_max_size'])
		self._bulks = {}

		self._timeout = float(self.Config['timeout'])
		self._started = True

		self.Loop = app.Loop

		self.PubSub = app.PubSub
		self.PubSub.subscribe("Application.run!", self._start)
		self.PubSub.subscribe("Application.exit!", self._on_exit)

		self._futures = []
		for url_position, url in enumerate(self.NodeUrls):

			# TODO: Is this correct?
			# The first url in the list is the preferred one,
			# the other urls are backups
			is_preferred = True
			# is_preferred = (url_position == 0)

			for i in range(self._loader_per_url):
				self._futures.append((url, None, is_preferred))

		# The preferred loaders are the ones that
		# connect to the first configured node URL
		self.RunOnlyPreferredLoaders = True

		self.FailLogMaxSize = int(self.Config['fail_log_max_size'])

		# Precise error handling
		if self.Config.getboolean("precise_error_handling"):
			self.FilterPath = "errors,took,items.*.error,items.*._id,items.*._index"
		else:
			self.FilterPath = "errors,took,items.*.error,items.*._index"

		if self.Config.getboolean("log_failed_documents"):
			self.LogFailedDocuments = True

		else:
			self.LogFailedDocuments = False

		# Create metrics counters
		metrics_service = app.get_service('asab.MetricsService')
		self.InsertMetric = metrics_service.create_counter(
			"elasticsearch.insert",
			init_values={
				"ok": 0,
				"fail": 0,
			}
		)
		self.QueueMetric = metrics_service.create_gauge(
			"elasticsearch.outputqueue",
			init_values={
				"size": 0,
			}
		)

		# ES common response codes
		self.ESResponseCodes = {
			200: "A resource was modified successfully",
			201: "A resource was created",
			400: "Request could not be processed/Attempted operation on closed index",
			401: "Unauthorized",
			403: "Index is read only, operation forbidden",
			404: "Resource could not be found",
			429: "Elasticsearch is overloaded",
		}

	def get_url(self):
		"""
		:return: list of URLS of nodes connected to the cluster

		"""
		return random.choice(self.NodeUrls)


	def get_session(self):
		"""
		Returns the aiohttp Client Session

		:return:
		"""
		return aiohttp.ClientSession(headers=self.Headers)


	def consume(self, index, data_feeder_generator, bulk_class=ElasticSearchBulk):
		"""
		Checks the content of data_feeder_generator and bulk and if There is data to be send it calls enqueue method.

		**Parameters**

		index :

		data_feeder_generator :

		bulk_class=ElasticSearchBulk :
				creates a instance of the ElasticSearchBulk class

		"""
		if data_feeder_generator is None:
			return

		bulk = self._bulks.get(index)
		if bulk is None:
			bulk = bulk_class(self, index, self._bulk_out_max_size)
			self._bulks[index] = bulk

		if bulk.consume(data_feeder_generator):
			# Bulk is ready, schedule to be send
			del self._bulks[index]
			self.enqueue(bulk)


	def _start(self, event_name):
		self.PubSub.subscribe("Application.tick!", self._on_tick)
		self._on_tick("simulated!")


	async def _on_exit(self, event_name):
		# Wait till the queue is empty
		self.flush(forced=True)
		while self._output_queue.qsize() > 0:
			self.flush(forced=True)
			await asyncio.sleep(1)
			if self._output_queue.qsize() > 0:
				L.warning(
					"Still have items in bulk output queue",
					struct_data={
						"output_queue_size": self._output_queue.qsize(),
					}
				)

		self._started = False

		# Wait till the _loader() terminates (one after another)
		pending = [item[1] for item in self._futures]
		self._futures = []
		while len(pending) > 0:
			# By sending None via queue, we signalize end of life
			await self._output_queue.put(None)
			done, pending = await asyncio.wait(pending, return_when=asyncio.FIRST_COMPLETED)


	def _on_tick(self, event_name):
		self.QueueMetric.set("size", int(self._output_queue.qsize()))

		for i in range(len(self._futures)):

			# 1) Check for exited futures
			url, future, is_preferred = self._futures[i]
			if future is not None and future.done():

				# Ups, _loader() task crashed during runtime, we need to restart it
				try:
					future.result()

				except Exception as e:
					L.exception(
						"Elasticsearch issue detected, will retry shortly",
						struct_data={"reason": e},
					)

				self._futures[i] = (url, None, is_preferred)

			# 2) Start _loader() futures that are exited
			if self._started:
				url, future, is_preferred = self._futures[i]

				if future is None:

					# Run only the preferred loaders?
					if not is_preferred and self.RunOnlyPreferredLoaders:
						continue

					future = asyncio.ensure_future(self._loader(url, is_preferred))
					self._futures[i] = (url, future, is_preferred)

		self.flush()


	def flush(self, forced=False):
		"""
		It goes through the list of bulks and calls enqueue for each of them.

		**Parameters**

		forced : bool, default = False

		"""
		aged = []
		current_time = self.App.time()

		for index, bulk in self._bulks.items():

			if bulk is None:
				continue

			bulk.Aging += 1

			if (bulk.Aging >= self.MaxBulkAge) or forced:
				aged.append(index)
				continue

			# The maximum lifespan of the bulk was exceeded
			if (current_time - bulk.CreatedAt) >= self.BulkLifespan:
				aged.append(index)
				continue

		for index in aged:
			bulk = self._bulks.pop(index)
			self.enqueue(bulk)


	def enqueue(self, bulk):
		"""
		Properly enqueue the bulk.

		**Parameters**

		bulk :

		"""
		self._output_queue.put_nowait(bulk)

		# Signalize need for throttling
		if self._output_queue.qsize() >= self._output_queue_max_size:  # Hotfix: There should be just ==, but _loader tasks are asychronous, investigate
			# This PubSub message is meant primarily for Elasticsearch Sinks that are attached to this connection
			self.PubSub.publish("ElasticSearchConnection.pause!", self)


	async def _loader(self, url, is_preferred):

		async with self.get_session() as session:

			# Preflight check
			try:
				async with session.get(
					url + "_cluster/health",
					ssl=self.SSLContext,
				) as resp:
					await resp.json()
					if resp.status != 200:
						L.error(
							"Cluster is not ready",
							struct_data={
								"status": resp.status,
								"reason": self.ESResponseCodes.get(resp.status, resp.status),
							},
						)
						await asyncio.sleep(5)  # Throttle a bit before next try
						return

			except aiohttp.client_exceptions.ServerDisconnectedError:
				L.error(
					"Cluster is not ready.",
					struct_data={"reason": "Server disconnected or not ready"}
				)
				await asyncio.sleep(5)  # Throttle a bit before next try
				return

			except OSError as e:
				L.error(
					"Cluster is not ready",
					struct_data={"reason": e}
				)
				await asyncio.sleep(5)  # Throttle a bit before next try
				return

			except aiohttp.client_exceptions.ContentTypeError as e:
				L.error(
					"Failed communication.",
					struct_data={"reason": e}
				)
				await asyncio.sleep(20)  # Throttle a lot before next try
				return

			except GeneratorExit as e:
				L.info(
					"Generator exited",
					struct_data={"reason": e}
				)
				return

			# Push bulks into the ElasticSearch
			while self._started:
				bulk = await self._output_queue.get()

				if bulk is None:
					break

				if self._output_queue.qsize() == self._output_queue_max_size - 1:
					# This PubSub message is meant primarily for Elasticsearch Sinks that are attached to this connection
					self.PubSub.publish("ElasticSearchConnection.unpause!", self)

				sucess = await bulk.upload(url, session, self.SSLContext, self._timeout)

				if not sucess:
					# Requeue the bulk for another delivery attempt to ES
					self.enqueue(bulk)

					# Allow others loaders to process the event
					if is_preferred:
						self.RunOnlyPreferredLoaders = False

					await asyncio.sleep(5)  # Throttle a bit before next try
					break  # Exit the loader (new will be started automatically)

				else:

					# Send bulks only to the preferred nodes again
					if is_preferred and not self.RunOnlyPreferredLoaders:
						self.RunOnlyPreferredLoaders = True

					# Exit the loader if it is not preferred
					if not is_preferred and self.RunOnlyPreferredLoaders:
						return

				# Make sure the memory is emptied
				bulk.Items = []


def get_url_list(urls):
	server_urls = []
	for url in urls:
		scheme, netloc, path = parse_url(url)

		server_urls += [
			urllib.parse.urlunparse((scheme, netloc, path, None, None, None))
			for netloc in netloc.split(';')
		]

	return server_urls


def parse_url(url):
	parsed_url = urllib.parse.urlparse(url)
	url_path = parsed_url.path
	if not url_path.endswith("/"):
		url_path += "/"

	return parsed_url.scheme, parsed_url.netloc, url_path


def section_has_ssl_option(config_section_name):
	"""
	Checks if cert, key, cafile, capath, cadata etc. appears in section's items
	"""
	for item in asab.Config.options(config_section_name):
		if item in SSLContextBuilder.ConfigDefaults:
			return True
	return False


def build_headers(username, password, api_key):

	# Check configurations
	if username != '' and username is not None and api_key != '' and api_key is not None:
		raise ValueError("Both username and API key can't be specified. Please choose one option.")

	headers = {
		'Content-Type': 'application/json',
	}

	# Build headers
	if username != '' and username is not None:
		auth = aiohttp.BasicAuth(username, password)
		headers['Authorization'] = auth.encode()

	elif api_key != '' and api_key is not None:
		headers['Authorization'] = 'ApiKey {}'.format(api_key)

	return headers
