import logging

import psycopg2

from ..abc.source import TriggerSource


L = logging.getLogger(__name__)


class PostgreSQLSource(TriggerSource):

	ConfigDefaults = {
		'query': ''
	}

	def __init__(self, app, pipeline, connection, id=None, config=None):
		super().__init__(app, pipeline, id=id, config=config)
		self.Loop = app.Loop
		self._connection = pipeline.locate_connection(app, connection)
		self._query = self.Config['query']
		self.App = app


	async def cycle(self):
		await self._connection.ConnectionEvent.wait()
		try:
			async with self._connection.acquire() as connection:
				async with connection.cursor() as cur:
					await cur.execute(self._query)
					event = {}
					while True:
						await self.Pipeline.ready()
						row = await cur.fetchone()
						if row is None:
							break

						# Transform row to an event object
						for i, val in enumerate(row):
							event[cur.description[i][0]] = val

						# Pass event to the pipeline
						await self.process(event)
					await cur.execute("COMMIT;")
		except (psycopg2.InternalError, psycopg2.ProgrammingError, psycopg2.OperationalError) as e:
			if e.args[0] in self._connection.RetryErrors:
				L.warn("Recoverable error '{}' occurred in PostgresSource. Retrying.".format(e.args[0]))
			raise e
