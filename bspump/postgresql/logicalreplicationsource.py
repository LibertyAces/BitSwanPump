import logging
from ..abc.source import Source
import asyncio
import psycopg2
import psycopg2.extras
import aiopg
import json
import asyncio
#

L = logging.getLogger(__name__)

#

class PostgreSQLLogicalReplicationSource(Source):
	'''
	'''

	ConfigDefaults = {
		'slot_name': '',
		'output_plugin': '',
	}
	
	# output example
	#table public.user_location: INSERT: user_id[integer]:11 lat[double precision]:55 lon[double precision]:13

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
		conn = psycopg2.connect(self.DSN,
			connection_factory=psycopg2.extras.LogicalReplicationConnection)
		self.Cursor = conn.cursor()
		try:
			self.Cursor.start_replication(slot_name=self.SlotName, decode=True)
		except psycopg2.ProgrammingError:
			self.Cursor.create_replication_slot(self.SlotName, output_plugin=self.OutputPlugin)
			self.Cursor.start_replication(slot_name=self.SlotName, decode=True)

		worker = self.ProactorService.execute(self.stream_data)

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
			worker.result()



		