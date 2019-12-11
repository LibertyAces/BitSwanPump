import asyncio
import json
import logging

import psycopg2
import psycopg2.extras

from ..abc.source import Source

#

L = logging.getLogger(__name__)

#


class PostgreSQLLogicalReplicationSource(Source):
	'''
		This is the source, which reads Postgres WAL-file and
		produces events `INSERT`, `DELETE` or `UPDATE`.
		By default it uses `wal2json` postgresql plugin
		and it is not preinstalled. Here are the steps, how to install it.
		`git clone https://github.com/eulerto/wal2json`
		`cd wal2json`
		`make`
		`make install`
		Then update postgresql.conf with lines:
		```
		############ REPLICATION ##############
		# MODULES
		shared_preload_libraries = 'wal2json'

		# REPLICATION
		wal_level = logical
		max_wal_senders = 4
		max_replication_slots = 4
		```
		Then restart postgres:
		`sudo service postgresql restart`

		You can use a different plug-in, but you have to override `decode()`.
	'''

	ConfigDefaults = {
		'slot_name': '',
		'output_plugin': 'wal2json',
	}


	def __init__(self, app, pipeline, connection, id=None, config=None):
		super().__init__(app, pipeline, id=id, config=config)
		self.Loop = app.Loop
		self.ConnectionGeneral = pipeline.locate_connection(app, connection)
		self.DSN = self.ConnectionGeneral.build_dsn()
		self.SlotName = self.Config['slot_name']
		self.OutputPlugin = self.Config['output_plugin']
		self.Queue = asyncio.Queue(loop=self.Loop)
		self.ProactorService = app.get_service("asab.ProactorService")
		self.Running = True


	def decode(self, message):
		'''
			Override it if you use a different plug-in
			or you want the output in non-dictionary form.
		'''
		message = json.loads(message)
		return message


	def stream_data(self):
		while True:
			if not self.Running:
				return False

			mes = self.Cursor.read_message()
			if mes is not None:
				self.Queue.put_nowait(({}, self.decode(mes.payload)))

		return True



	async def main(self):
		await self.Pipeline.ready()

		conn = psycopg2.connect(
			self.DSN,
			connection_factory=psycopg2.extras.LogicalReplicationConnection)
		self.Cursor = conn.cursor()

		try:
			self.Cursor.start_replication(slot_name=self.SlotName, decode=False)
		except psycopg2.ProgrammingError:
			self.Cursor.create_replication_slot(self.SlotName, output_plugin=self.OutputPlugin)
			self.Cursor.start_replication(slot_name=self.SlotName, decode=False)

		self.ProactorService.execute(self.stream_data)

		try:
			while True:
				context, event = await self.Queue.get()
				await self.process(event, context={})
				self.Queue.task_done()

		except asyncio.CancelledError:
			if self.Queue.qsize() > 0:
				self.Running = False
				L.warning("'{}' stopped with {} events in a queue".format(self.locate_address(), self.Queue.qsize()))

		finally:
			self.Running = False
