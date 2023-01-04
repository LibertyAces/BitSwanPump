import asyncio
import logging
import pymongo

from ..abc.source import Source

#

L = logging.getLogger(__name__)

#


class MongoDBChangeStreamSource(Source):
	'''
		`MongoDBChangeStreamSource` listens to the specified `Database`
		and (optionally) `Collection` (if not configured, the events are aggregated
		from all collections). The output are `update`, `insert`, `delete`,
		`invalidate`, `dropDatabase`, `drop`, `rename`, `replace` events.
		Examples of events you can find here: https://docs.mongodb.com/manual/reference/change-events/
		WARNING! Make sure, that version of MongoDB is >= 4.0.0 and
		replica set is enabled.
	'''

	ConfigDefaults = {
		'database': '',
		'collection': '',
		'full_document': '',
	}


	def __init__(self, app, pipeline, connection, id=None, config=None):
		super().__init__(app, pipeline, id=id, config=config)
		self.Connection = pipeline.locate_connection(app, connection)
		self.Database = self.Config['database']
		self.Collection = self.Config['collection']
		self.FullDocument = self.Config['full_document']
		if self.FullDocument == '':
			self.FullDocument = None
		if self.Collection == '':
			self.Collection = None


	async def main(self):
		running = True
		await self.Pipeline.ready()
		db = self.Connection.Client[self.Database]
		if self.Collection is None:
			if self.FullDocument is None:
				stream = db.watch()
			else:
				stream = db.watch(full_document=self.FullDocument)
		else:
			if self.FullDocument is None:
				stream = db[self.Collection].watch()
			else:
				stream = db[self.Collection].watch(full_document=self.FullDocument)

		while True:
			if not running:
				await stream.close()
				break
			try:
				event = await stream.next()
				await self.process(event, context={})

			except asyncio.CancelledError:
				running = False
			except pymongo.errors.OperationFailure as e:
				L.warning("Recoverable error encountered while reading changestream: {}.".format(e))
				continue
