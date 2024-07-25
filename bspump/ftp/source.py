import asyncio
import logging

from aioftp import StatusCodeError

from bspump.abc.source import TriggerSource

###

L = logging.getLogger(__name__)

###


class FTPSource(TriggerSource):

	ConfigDefaults = {
		'remote_path': '/',
		'mode': 'r',  # r = read, p = pop
	}

	def __init__(self, app, pipeline, connection, id=None, config=None):
		"""
		Description:

		**Parameters**

		app : Application
			Name of the Application

		pipeline :

		connection :

		id : ID, default = None

		config : JSON, default = None


		"""
		super().__init__(app, pipeline, id=id, config=config)
		self.Loop = app.Loop
		self.Pipeline = pipeline
		self.Queue = asyncio.Queue()
		self.Connection = pipeline.locate_connection(app, connection)
		self.Filename = self.Config.get('filename', None)
		self.RemotePath = self.Config['remote_path']
		self._conn_future = None
		self.list_future = None

	async def list_files(self):

		if self.Queue.qsize() == 0:
			self.list_future = None

		# Connect to the client
		self.client = await self.Connection.connect()

		# If the filename is specified then add only filename to queue else add the
		# full path into queue.
		if self.Filename is not None:
			tmp = self.RemotePath + '/' + self.Filename
			self.Queue.put_nowait(tmp)
		else:
			# if there are directories then don't add them to queue.
			for path, info in (await self.client.list(self.RemotePath)):
				try:
					if info['type'] == 'dir':
						continue
					else:
						self.Queue.put_nowait(path)
				except asyncio.queues.QueueFull:
					L.warning("Queue has reached it's limit")

	async def inbound(self):
		while True:
			try:
				path = await self.Queue.get()
				async with self.client.download_stream(path) as stream:
					async for block in stream.iter_by_block():
						await self.process(block)

				if self.Queue.empty():
					await self.client.quit()
					self._conn_future = None
					break
			except (ConnectionResetError, StatusCodeError) as exception:
				L.exception(exception)

	async def cycle(self):
		if self.list_future:
			pass

		else:
			self.list_future = asyncio.ensure_future(
				self.list_files(),
			)

		if self._conn_future:
			pass

		else:
			pass
			self._conn_future = asyncio.ensure_future(
				self.inbound(),
			)
			await self._conn_future
