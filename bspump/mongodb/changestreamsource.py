import logging
from ..abc.source import Source
import asyncio
import pymongo
#

L = logging.getLogger(__name__)

#

class MongoDBChangeStreamSource(Source):
	'''
		Make sure, that version of MongoDB is >= 4.0.0 and
		replica set is enabled.
		TODO: add queries to match. 
	'''

	ConfigDefaults = {
		'database':'',
		'collection':'',
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



		