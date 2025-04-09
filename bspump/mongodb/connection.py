import logging

import asyncio

import motor.motor_asyncio
import pymongo

import asab

from ..abc.connection import Connection

#

L = logging.getLogger(__name__)

#


def data_feeder_update(event, _id):
	yield pymongo.UpdateOne(
		{"_id": _id},
		{
			"$set": event,
		},
		upsert=True
	)


class MongoDBBulk(object):
	"""
	Bulk to be inserted to MongoDB.
	"""

	def __init__(self, connection, collection_name, max_size):
		self.Collection = connection.Client[connection.Database][collection_name]
		self.Aging = 0
		self.Capacity = max_size
		self.Items = []
		self.InsertMetric = connection.InsertMetric
		self.CreatedAt = connection.App.time()


	def consume(self, data_feeder_generator):
		"""
		Appends all items in data_feeder_generator to Items list. Consumer also resets Aging and Capacity.

		**Parameters**

		data_feeder_generator : list
				list of our data that will be passed to a generator and later Uploaded to MongoDB.

		:return: self.Capacity <= 0

		"""
		for item in data_feeder_generator:
			self.Items.append(item)
			self.Capacity -= 1

		# Reset the aging so the bulk can be filled up to its capacity
		self.Aging = 0

		# Was the capacity of the bulk exceeded?
		return self.Capacity <= 0


	async def _get_data_from_items(self):

		for item in self.Items:
			yield item


	async def upload(self):

		if len(self.Items) == 0:
			return

		try:
			self.Collection.bulk_write(self.Items)
			self.InsertMetric.add("ok", len(self.Items))

		except Exception as e:
			return self.full_error_callback(self.Items, e)
			self.InsertMetric.add("fail", len(self.Items))
			return False

		return True


	def full_error_callback(self, bulk_items, exception):
		L.exception(exception)
		return True


class MongoDBConnection(Connection):

	ConfigDefaults = {
		'uri': '',

		'output_queue_max_size': 10,
		'bulk_out_max_size': 1024,
		'bulk_lifespan': 30,  # Lifespan is the maximum time for bulk existence, per tick/second
		'max_bulk_age': 2,  # Age is when no event comes to the bulk, per tick/second

		'database': 'database',
	}

	def __init__(self, app, id=None, config=None):
		super().__init__(app, id=id, config=config)

		uri = self.Config.get('uri')

		if len(uri) == 0:
			uri = asab.Config.get('mongo', 'uri', fallback='')

		self.Client = motor.motor_asyncio.AsyncIOMotorClient(uri)
		self.Database = self.Config['database']

		# The lifespan of bulks (per second)
		self.BulkLifespan = self.Config.getint('bulk_lifespan')

		# Maximum age of bulks (per second)
		self.MaxBulkAge = self.Config.getint('max_bulk_age')

		self._output_queue_max_size = int(self.Config['output_queue_max_size'])
		self._output_queue = asyncio.Queue()
		self._bulk_out_max_size = int(self.Config['bulk_out_max_size'])
		self._bulks = {}
		self._started = True
		self._future = None

		self.PubSub = app.PubSub
		self.PubSub.subscribe("Application.run!", self._start)
		self.PubSub.subscribe("Application.exit!", self._on_exit)

		# Create metrics counters
		metrics_service = app.get_service('asab.MetricsService')
		self.InsertMetric = metrics_service.create_counter(
			"mongodb.insert",
			init_values={
				"ok": 0,
				"fail": 0,
			}
		)
		self.QueueMetric = metrics_service.create_gauge(
			"mongodb.outputqueue",
			init_values={
				"size": 0,
			}
		)


	def consume(self, collection_name, data_feeder_generator, bulk_class=MongoDBBulk):
		"""
		Checks the content of data_feeder_generator and bulk and if There is data to be send it calls enqueue method.

		**Parameters**

		collection_name :

		data_feeder_generator :

		bulk_class=MongoDBBulk :

		"""
		if data_feeder_generator is None:
			return

		bulk = self._bulks.get(collection_name)

		if bulk is None:
			bulk = bulk_class(self, collection_name, self._bulk_out_max_size)
			self._bulks[collection_name] = bulk

		if bulk.consume(data_feeder_generator):
			# Bulk is ready, schedule to be send
			del self._bulks[collection_name]
			self.enqueue(bulk)


	def _start(self, event_name=None):
		self.PubSub.subscribe("Application.tick!", self._on_tick)
		self._on_tick()


	async def _on_exit(self, event_name=None):

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

		# Wait for the future
		if self._future is not None:
			await self._future


	def _on_tick(self, event_name=None):
		self.QueueMetric.set("size", int(self._output_queue.qsize()))

		# 1) Check if the future has exited
		if self._future is not None:

			if self._future.done():

				# Ups, _loader() task crashed during runtime, we need to restart it
				try:
					self._future.result()

				except Exception as e:
					L.exception(
						"MongoDB issue detected, will retry shortly",
						struct_data={"reason": e},
					)

				self._future = None

		# 2) Start the future
		if self._started:

			if self._future is None:
				self._future = asyncio.ensure_future(self._loader())

		self.flush()


	def flush(self, forced=False):
		"""
		It goes through the list of bulks and calls enqueue for each of them.

		**Parameters**

		forced : bool, default = False

		"""
		aged = []
		current_time = self.App.time()

		for collection_name, bulk in self._bulks.items():

			if bulk is None:
				continue

			bulk.Aging += 1

			if (bulk.Aging >= self.MaxBulkAge) or forced:
				aged.append(collection_name)
				continue

			# The maximum lifespan of the bulk was exceeded
			if (current_time - bulk.CreatedAt) >= self.BulkLifespan:
				aged.append(collection_name)
				continue

		for collection_name in aged:
			bulk = self._bulks.pop(collection_name)
			self.enqueue(bulk)


	def enqueue(self, bulk):
		"""
		Properly enqueue the bulk.

		**Parameters**

		bulk :

		"""
		self._output_queue.put_nowait(bulk)

		# Signalize need for throttling
		if self._output_queue.qsize() >= self._output_queue_max_size:
			self.PubSub.publish("MongoDBConnection.pause!", self)


	async def _loader(self):

		# Push bulks into the MongoDB
		while self._started:
			bulk = await self._output_queue.get()

			if bulk is None:
				break

			if self._output_queue.qsize() == self._output_queue_max_size - 1:
				self.PubSub.publish("MongoDBConnection.unpause!", self)

			sucess = await bulk.upload()

			if not sucess:
				# Requeue the bulk for another delivery attempt to ES
				self.enqueue(bulk)

				await asyncio.sleep(5)  # Throttle a bit before next try
				break  # Exit the loader (new will be started automatically)

			# Make sure the memory is emptied
			bulk.Items = []
