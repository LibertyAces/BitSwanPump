import logging

import clickhouse_driver

from ..abc.sink import Sink

#

L = logging.getLogger(__name__)

#


class ClickHouseSink(Sink):

	ConfigDefaults = {
		"host": "",
		"user": "",
		"password": "",

		"database": "",
		"table": "",
		"schema": "",
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

		self.BulkSize = self.Config.getint("bulk_size")
		self.Bulk = []
		self.BulkLen = 0

		self.Database = self.Config.get("database")
		self.Table = self.Config.get("table")
		self.Schema = self.Config.get("schema")

		self.Client.execute('CREATE DATABASE IF NOT EXISTS {}'.format(self.Database))
		self.Client.execute("CREATE TABLE IF NOT EXISTS {}.{} ({}) ENGINE = Memory".format(
			self.Database, self.Table, self.Schema)
		)


	def process(self, context, event):
		self.Bulk.append(event)
		self.BulkLen += 1

		if self.BulkLen >= self.BulkSize:
			self._insert_bulk_to_database()
			self.Bulk = []
			self.BulkLen = 0


	def _insert_bulk_to_database(self):
		self.Client.execute('INSERT INTO {}.{} VALUES'.format(
			self.Database, self.Table), self.Bulk
		)
