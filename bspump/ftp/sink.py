from ..abc.sink  import Sink

class FtpSink(Sink): #TODO establish sink module

	def __init__(self, app, pipeline, connection, id=None, config=None):
		super().__init__(app, pipeline, id=id, config=config)

		self._connection = pipeline.locate_connection(app, connection)

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


# import asyncio, asyncssh, sys
#
# async def run_client():
#     async with asyncssh.connect('localhost') as conn:
#         async with conn.create_process('bc') as process:
#             for op in ['2+2', '1*2*3*4', '2^32']:
#                 process.stdin.write(op + '\n')
#                 result = await process.stdout.readline()
#                 print(op, '=', result, end='')
#
# try:
#     asyncio.get_event_loop().run_until_complete(run_client())
# except (OSError, asyncssh.Error) as exc:
#     sys.exit('SSH connection failed: ' + str(exc))