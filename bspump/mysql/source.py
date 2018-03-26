import asab
import asyncio
from ..abcproc import Source


class MySQLRowSource(Source):
	
	def __init__(self, app, pipeline, connection, id=None, config=None):
		super().__init__(app, pipeline, id=id, config=config)
		self._connection = pipeline.locate_connection(app, connection)
		self._query = self.Config['query']


	async def start(self):
		# Listen for connection open

		# Await MySQL rows
		await self._connection.open()

		async with self._connection.acquire() as conn:
			async with conn.cursor() as cur:
				await cur.execute(self._query)
				row = {}
				while True:
					await self.Pipeline.ready()
					_r = await cur.fetchone()
					if _r is None:
						break
					for i, val in enumerate(_r):
						row[cur.description[i][0]] = val
					self.process(row)


		await self._connection.close()

