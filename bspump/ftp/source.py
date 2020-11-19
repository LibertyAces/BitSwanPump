import asyncio
import logging
from bspump.abc.source import TriggerSource
import aioftp
###

L = logging.getLogger(__name__)

###


class FTPSource(TriggerSource):

	ConfigDefaults = {
		'remote_path': '/',
		'mode': 'r',  # r = read, p = pop
	}

	def __init__(self, app, pipeline, connection,id=None, config=None):
		super().__init__(app, pipeline, id=id, config=config)
		self.Loop = app.Loop
		self.Pipeline = pipeline
		self.Queue = asyncio.Queue(loop=self.Loop)

		self.Connection = pipeline.locate_connection(app, connection)

		self.Filename= self.Config.get('filename',None)
		print(self.Filename)
		self.RemotePath = self.Config['remote_path']
		self._conn_future = None
		self.list_future = None

	async def list_files(self):

		if self.Queue.qsize() == 0:
			self.list_future = None

		#conenct to client
		self.client = await self.Connection.run1()

		for path, info in (await self.client.list()):
			print(path)
			self.Queue.put_nowait(path)

	async def inbound(self):
		while True:
			try:
				path = await self.Queue.get()
				if self.Filename is not None:
					path = self.Filename

				#get connection object
				self.client = await self.Connection.run1()

				async with self.client.download_stream(path) as stream:
					async for block in stream.iter_by_block():
						await self.process(block)

				if self.Queue.empty():
					print()
					print("Done!")
					await stream.finish()
					await self.client.quit()
					self._conn_future = None
					break
			except ConnectionResetError:
				pass

	async def cycle(self):
		if self.list_future:
			pass

		else:
			self.list_future = asyncio.ensure_future(
				self.list_files(),
				loop=self.Loop
			)

		if self._conn_future:
			pass

		else:
			pass
			self._conn_future = asyncio.ensure_future(
				self.inbound(),
				loop=self.Loop
			)


