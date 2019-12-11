import asyncio
import logging

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
	}


	def __init__(self, app, pipeline, connection, id=None, config=None):
		super().__init__(app, pipeline, id=id, config=config)
		self.Connection = pipeline.locate_connection(app, connection)
		self.Database = self.Config['database']
		self.Collection = self.Config['collection']
		if self.Collection == '':
			self.Collection = None


	async def main(self):
		running = True
		await self.Pipeline.ready()
		db = self.Connection.Client[self.Database]
		if self.Collection is None:
			stream = db.watch()
		else:
			stream = db[self.Collection].watch()

		while True:
			if not running:
				await stream.close()
				break
			try:
				event = await stream.next()
				await self.process(event, context={})

			except asyncio.CancelledError:
				running = False
