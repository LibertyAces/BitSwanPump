import logging
import asyncio
from .. import Source

#

L = logging.getLogger(__file__)

#


class FileLineSource(Source):

	ConfigDefaults = {
		'path': '',
	}

	def __init__(self, app, pipeline, id=None, config=None):
		super().__init__(app, pipeline, id=id, config=config)

		self.Loop = app.Loop

	async def process_file_coro(self):
		async def process_line_coro(line):
			self.process(line)

		try:
			with open(self.Config['path'], "rb") as f:
				for line in f:
					await asyncio.ensure_future(process_line_coro(line), loop=self.Loop)
		except IOError:
			L.error("The specified file {} could not be opened.".format(self.Config['path']))

	async def start(self):
		# Run the reading of the file
		asyncio.ensure_future(self.process_file_coro(), loop=self.Loop)


class FileBlockSource(Source):

	ConfigDefaults = {
		'path': '',
	}

	async def start(self):
		filename = self.Config['path']
		with open(filename, "rb") as f:
			event = f.read()

		self.process(event)
