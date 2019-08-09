import logging
from ..abc.source import Source
import asyncio

#

L = logging.getLogger(__name__)

#

class MongoDBChangeStreamSource(Source):

	ConfigDefaults = {
		'database':'',
		'collection':'',
	}
	

	def __init__(self, app, pipeline, connection, id=None, config=None):
		super().__init__(app, pipeline, id=id, config=config)
		self.Connection = pipeline.locate_connection(app, connection)
		self.Database = self.Config['database']
		self.Collection = self.Config['collection']
	

	async def main(self):
		running = True
		db = self.Connection.Client[self.Database]

		await self.Pipeline.ready()
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



		