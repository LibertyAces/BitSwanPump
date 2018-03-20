import os.path
import logging
import glob
import asyncio
import asab
from .. import Source
from .. import ProcessingError

#

L = logging.getLogger(__file__)

#

def _scan_for_file(path):
	if path is None: return None
	if path == "": return None

	filelist = glob.glob(path)
	filelist.sort()
	while len(filelist) > 0:
		fname = filelist.pop()
		if not os.path.isfile(fname): continue

		#TODO: Validate thru lsof ...

		return fname

	return None



class FileLineSource(Source):


	ConfigDefaults = {
		'path': '',
		'mode': 'rb',
	}


	def __init__(self, app, pipeline, id=None, config=None):
		super().__init__(app, pipeline, id=id, config=config)
		self.Loop = app.Loop
		self._future = None
		app.PubSub.subscribe("Application.tick/10!", self._on_health_check)

		self.path = self.Config['path']
		self.mode = self.Config['mode']


	def _on_health_check(self, message_type):
		if self._future is not None:
			if not self._future.done():
				# We are still processing a file
				return

			try:
				self._future.result()
			except:
				L.exception("Unexpected error when reading file")

			self._future = None

		assert(self._future is None)

		filename = _scan_for_file(self.path)
		if filename is None: return # No file to read
		self.path = "" # TODO: Enhance

		self._future = asyncio.ensure_future(
			self._read_file(filename, self.mode),
			loop=self.Loop
		)


	async def _read_file(self, filename, mode):
		await self.Pipeline.ready()

		try:
			if filename.endswith(".gz"):
				import gzip
				f = gzip.open(filename, mode)

			elif filename.endswith(".bz2"):
				import bz2
				f = bz2.open(filename, mode)

			elif filename.endswith(".xz") or filename.endswith(".lzma"):
				import lzma
				f = lzma.open(filename, mode)

			else:
				f = open(filename, mode)

		except:
			self.Pipeline.set_error(ProcessingError("The file '{}' could not be read.".format(filename)), None)
			return

		try:
			for line in f:
				await self.Pipeline.ready()
				self.process(line)
		finally:
			f.close()

		# Ensure that we iterate to a next file quickly
		self.Loop.call_soon(self._on_health_check, 'file.read!')


	async def start(self):
		self._on_health_check('pipeline.started!')


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
