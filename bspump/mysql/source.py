import asab
import asyncio
import logging
import aiomysql.cursors
from ..abc.source import TriggerSource
import pymysqlreplication

#

L = logging.getLogger(__name__)

#

class MySQLSource(TriggerSource):

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
		async with self._connection.acquire() as connection:
			try:
				async with connection.cursor(aiomysql.cursors.SSCursor) as cur:
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
			except BaseException as e:
				L.exception("Unexpected error when processing MySQL query.")


class MySQLBinaryLogSource(TriggerSource):

	ConfigDefaults = {
		'server_id': 1
	}
	
	def __init__(self, app, pipeline, connection, id=None, config=None):
		super().__init__(app, pipeline, id=id, config=config)
		self._connection = pipeline.locate_connection(app, connection)
		self.MySQLSettings = {
			'host': self._connection._host, 
			'port': self._connection._port, 
			'user': self._connection._user, 
			'passwd': self._connection._password, 
		}
		self.ServerId = int(self.Config['server_id'])
		self.Stream = pymysqlreplication.BinLogStreamReader(connection_settings=self.MySQLSettings, server_id=self.ServerId)


	async def cycle(self):
		await self.Pipeline.ready()
		for binlogevent in self.Stream:
			event = {}

			# General info
			event_type = binlogevent.__class__.__name__
			event['type'] = event_type
			event['@timestamp'] = binlogevent.timestamp
			event['log_position'] = binlogevent.packet.log_pos
			event['event_size'] = binlogevent.event_size
			event['read_bytes'] = binlogevent.packet.read_bytes

			# Specific info
			if event_type in ['DeleteRowsEvent', 'WriteRowsEvent', 'UpdateRowsEvent']:
				event['rows'] = binlogevent.rows
			
			if event_type == 'TableMapEvent':
				event['table_id'] = binlogevent.table_id
				event['schema'] = binlogevent.schema
				event['table'] = binlogevent.table
				event['columns'] = binlogevent.column_count

			if event_type == 'GtidEvent':
				event['commit'] = binlogevent.commit_flag
				event['GTID_NEXT'] = binlogevent.gtid

			if event_type == 'RotateEvent':
				event['position'] = binlogevent.position
				event['next_binlog_file'] = binlogevent.next_binlog
				
			if event_type == 'XidEvent':
				event['transaction_id'] = binlogevent.xid
			
			if event_type == 'HeartbeatLogEvent':
				event['current_binlog'] = binlogevent.ident

			if event_type == 'QueryEvent':
				event['schema'] = binlogevent.schema
				event['execution_time'] = binlogevent.execution_time
				event['query'] = binlogevent.query

			if event_type == 'BeginLoadQueryEvent':
				event['file_id'] = binlogevent.file_id
				event['block_data'] = binlogevent.block_data

			if event_type == 'ExecuteLoadQueryEvent':
				event['slave_proxy_id'] = binlogevent.slave_proxy_id
				event['execution_time'] = binlogevent.execution_time
				event['schema_length'] = binlogevent.schema_length
				event['error_code'] = binlogevent.error_code
				event['status_vars_length'] = binlogevent.status_vars_length
				event['file_id'] = binlogevent.file_id
				event['start_pos'] = binlogevent.start_pos
				event['end_pos'] = binlogevent.end_pos
				event['dup_handling_flags'] = binlogevent.dup_handling_flags

			if event_type == 'IntvarEvent':
				event['type'] = binlogevent.type
				event['value'] = binlogevent.value

			await self.process(event)
