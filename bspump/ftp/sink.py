from ..abc.sink  import Sink

ConfigDefaults = {

		'remote_path': '',
		'local_path': '',
		'preserve': 'False',
		'recurse': 'False',

}

class FTPSink(Sink): #TODO establish FTP sink

	def __init__(self, app, pipeline, connection, id=None, config=None):
		super().__init__(app, pipeline, id=id, config=config)

		self._connection = pipeline.locate_connection(app, connection)

		self._rem_path = self.Config['remote_path']
		self._loc_path = self.Config['local_path']
		self._preserve = bool(self.Config['preserve'])
		self._recurse = bool(self.Config['recurse'])

		app.PubSub.subscribe("FTPConnection.pause!", self._connection_throttle)
		app.PubSub.subscribe("FTPConnection.unpause!", self._connection_throttle)


	def _connection_throttle(self, event_name, connection):
		if connection != self._connection:
			return

		if event_name == "FTPConnection.pause!":
			self.Pipeline.throttle(self, True)
		elif event_name == "FTPConnection.unpause!":
			self.Pipeline.throttle(self, False)
		else:
			raise RuntimeError("Unexpected event name '{}'".format(event_name))

	def process(self, context, event):
		event = self.main_sink() # not sure, if this is allright...
		self._connection.consume(event)

	async def main_sink(self):
		async with self._connection.acquire_connection() as connection:
			async with connection.start_sftp_client() as sftp:
				try:
					await sftp.mkdir(self._rem_path)
				except asyncssh.SFTPError:
					pass
				await sftp.put(self._loc_path, remotepath=self._rem_path, preserve=self._preserve, recurse=self._recurse)



