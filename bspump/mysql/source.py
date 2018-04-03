import asab
import asyncio
import logging
from ..abc.source import Source

#

L = logging.getLogger(__name__)

#

class MySQLSource(Source):
	
	def __init__(self, app, pipeline, connection, id=None, config=None):
		super().__init__(app, pipeline, id=id, config=config)
		self.Loop = app.Loop
		self._connection = pipeline.locate_connection(app, connection)
		self._query = self.Config['query']
		self.App = app


	async def main(self):

		# Await connection open
		await self._connection.ConnectionEvent.wait()
		try:
			async with self._connection.acquire() as conn:
				try:
					async with conn.cursor() as cur:
						await cur.execute(self._query)
						event = {}
						while True:
							await self.Pipeline.ready()
							row = await cur.fetchone()
							if row is None:
								break

							# This is how event is transformed to a dictionary
							for i, val in enumerate(row):
								event[cur.description[i][0]] = val
							self.process(event)
				except Exception as e:
					L.exception("Unexpected error when processing MySQL query.")
		except Exception as e:
			L.exception("Couldn't acquire connection")
		self.App.stop()
