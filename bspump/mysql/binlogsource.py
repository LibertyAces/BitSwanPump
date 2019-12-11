import asyncio
import logging

import pymysqlreplication

from ..abc.source import Source

#

L = logging.getLogger(__name__)

#


class MySQLBinaryLogSource(Source):

	ConfigDefaults = {
		'server_id': 1,
		'log_file': '',  # name of the first log file
		'log_pos': 4,
		'extract_events':
			"""
			DeleteRowsEvent
			UpdateRowsEvent
			WriteRowsEvent
			"""
	}

	'''
	Before you started using it, make sure that
	my.cnf configuration file contains following lines:

	[mysqld]
	server-id		 = 1
	log_bin			 = /var/log/mysql/mysql-bin.log
	expire_logs_days = 10
	max_binlog_size  = 100M
	binlog-format    = row #Very important if you want to receive write, update and delete row events

	Also don't forget to restart the server after changing the config file.

	By default, the it picks the last log file, but you can specify your own, you can find it in /var/log/mysql/ folder, so it
	will process all files, started from specified one.

	The source extracts events from MySQL binary log. By default it extracts only [DeleteRowsEvent, UpdateRowsEvent, WriteRowsEvent],
	but you can extend the list in configuration with [QueryEvent, RotateEvent,StopEvent,FormatDescriptionEvent,XidEvent,
		GtidEvent,BeginLoadQueryEvent,ExecuteLoadQueryEvent,TableMapEvent,HeartbeatLogEvent]

	Examples:
	UpdateRowsEvent event:
		{
			'@timestamp': 1551791161,
			'event_size': 47,
			'log_position': 1251,
			'read_bytes': 13,
			'rows': [
				{'after_values': {'data': 'World', 'data2': 'Hello', 'id': 1}},
				{'before_values': {'data': 'Hello', 'data2': 'World', 'id': 1}}
			],
			'type': 'UpdateRowsEvent'
		}

	DeleteRowsEvent event:
		{
			'@timestamp': 1551791168,
			'event_size': 29,
			'log_position': 1525,
			'read_bytes': 12,
			'rows': [{'values': {'data': 'World', 'data2': 'Hello', 'id': 1}}],
			'type': 'DeleteRowsEvent'
		}

	WriteRowsEvent event:
		{
			'@timestamp': 1551791153,
			'event_size': 29,
			'log_position': 959,
			'read_bytes': 12,
			'rows': [{'values': {'data': 'Hello', 'data2': 'World', 'id': 1}}],
			'type': 'WriteRowsEvent'
		}

	'''


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
		self.ProactorService = app.get_service("asab.ProactorService")

		self.ServerId = int(self.Config['server_id'])
		self.LogFile = self.Config['log_file']
		self.LogPos = int(self.Config['log_pos'])

		if self.LogFile == '':
			self.LogFile = None
			self.LogPos = None

		extract_events = []
		lines = self.Config["extract_events"].split('\n')
		for line in lines:
			line_core = "".join(line.split())
			if len(line_core) == 0:
				continue
			extract_events.append(line_core)

		self.ExtractEvents = frozenset(extract_events)
		self.Loop = app.Loop
		self.Queue = asyncio.Queue(loop=self.Loop)
		self.Running = True
		self.Stream = None


	def stream_data(self):
		self.Stream = pymysqlreplication.BinLogStreamReader(
			connection_settings=self.MySQLSettings,
			server_id=self.ServerId,
			log_file=self.LogFile,
			log_pos=self.LogPos,
			resume_stream=True
		)

		for binlogevent in self.Stream:

			if not self.Running:
				return False

			event = {}

			event_type = binlogevent.__class__.__name__

			if event_type not in self.ExtractEvents:
				continue

			# General info
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

			self.Queue.put_nowait(({}, event))
		return True


	async def main(self):
		worker = self.ProactorService.execute(self.stream_data)

		try:
			while True:
				await self.Pipeline.ready()
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
