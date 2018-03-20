import asyncio
from .. import Source

class FileBlockSource(Source):


	ConfigDefaults = {
		'path': '',
		'mode': 'rb',
	}


	def __init__(self, app, pipeline, id=None, config=None):
		super().__init__(app, pipeline, id=id, config=config)
		self.Loop = app.Loop
		self._future = None


	async def _read_file(self):
		
		filename = self.Config['path']
		mode = self.Config['mode']

		await self.Pipeline.ready()

		with open(filename, mode) as f:
			event = f.read()

		self.process(event)



	async def start(self):
		self._future = asyncio.ensure_future(self._read_file(), loop=self.Loop)
