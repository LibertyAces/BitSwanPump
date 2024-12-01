import logging
import asyncio

import clickhouse_driver

from ..abc.source import TriggerSource

#

L = logging.getLogger(__name__)

#


class ClickHouseSource(TriggerSource):

	ConfigDefaults = {
		"host": "",
		"user": "",
		"password": "",

		"database": "",
		"table": "",
		"refresh": 1,
		"bulk_size": 1,
	}

	def __init__(self, app, pipeline, connection, id=None, config=None):
		super().__init__(app, pipeline, id=id, config=config)

		host = self.Config.get("host")
		user = self.Config.get("user")
		password = self.Config.get("password")

		if len(user) == 0:
			self.Client = clickhouse_driver.Client(
				host=host
			)

		else:
			self.Client = clickhouse_driver.Client(
				host=host, user=user, password=password
			)

		self.Database = self.Config.get("database")
		self.Table = self.Config.get("table")

		refresh = self.Config.getint("refresh")
		self.BulkSize = self.Config.getint("bulk_size")

		self.Client.execute("SET allow_experimental_live_view = 1")
		self.Client.execute("CREATE LIVE VIEW IF NOT EXISTS {}.{} WITH REFRESH {} AS SELECT *".format(
			self.Database, self.Table, refresh)
		)

		self.Running = True


	async def main(self):

		while self.Running:

			try:
				data = self.Client.execute("WATCH {}.{} LIMIT {};".format(
					self.Database, self.Table, self.BulkSize)
				)

				for item in data:
					await self.process(item, context={})

			except asyncio.CancelledError:
				self.Running = False
