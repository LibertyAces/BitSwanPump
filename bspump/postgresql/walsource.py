import logging
from ..abc.source import Source
import asyncio
import psycopg2
import psycopg2.extras
import aiopg
#

L = logging.getLogger(__name__)

#

class PostgreSQLWriteAheadLogSource(Source):
	'''
	'''

	ConfigDefaults = {
	}
	

	def __init__(self, app, pipeline, connection, id=None, config=None):
		super().__init__(app, pipeline, id=id, config=config)
		self.ConnectionGeneral = pipeline.locate_connection(app, connection)
		self.DSN = self.ConnectionGeneral.build_dsn()

	

	async def main(self):
		running = True
		await self.Pipeline.ready()
		
		self.Connection = await aiopg.connect(self.DSN, self.App.Loop)
		self.Cursor = await self.Connection.cursor(cursor_factory=psycopg2.extras.ReplicationCursor)
		while True:
			if not running:
				await self.Connection.close()
				break
			try:
				event = await self.Cursor.fetchone()
				print(event)
				await self.process(event, context={})

			except asyncio.CancelledError:
				running = False



		