import logging
from ..abc.source import TriggerSource
import pymysqlreplication

#

L = logging.getLogger(__name__)

#

class MySQLBinaryLogSource(TriggerSource):

	ConfigDefaults = {
		'server_id': 1
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

	Also make sure to restart the server after changing the config file.

	The source extracts UPDATE, DELETE, WRITE events from MySQL binary log
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
				event['rows'] = binlogevent.rows # it is a list
			
			await self.process(event)
