import abc
import os
import logging
import asyncio
import asab

from ..abc.source import TriggerSource
from .. import ProcessingError

from .globscan import _glob_scan

#

L = logging.getLogger(__file__)

#

class FileABCSource(TriggerSource):


	ConfigDefaults = {
		'path': '',
		'mode': 'rb',
		'newline': None,
		'post': 'move', # one of 'delete', 'noop' and 'move'
		'exclude': '', # glob of filenames that should be excluded (has precedence over 'include')
		'include': '', # glob of filenames that should be included
	}


	def __init__(self, app, pipeline, id=None, config=None):
		super().__init__(app, pipeline, id=id, config=config)

		self.path = self.Config['path']
		self.mode = self.Config['mode']
		self.newline = self.Config['newline']
		self.post = self.Config['post']
		if self.post not in ['delete', 'noop', 'move']:
			L.warning("Incorrect/unknown 'post' configuration value '{}' - defaulting to 'move'".format(self.post))
			self.post = 'move'
		self.include = self.Config['include']
		self.exclude = self.Config['exclude']


	async def cycle(self):
		filename = _glob_scan(self.path, exclude=self.exclude, include=self.include)
		if filename is None:
			self.Pipeline.PubSub.publish("bspump.file_source.no_files!")
			return # No file to read

		await self.Pipeline.ready()

		# Lock the file
		L.debug("Locking file '{}'".format(filename))
		locked_filename = filename + '-locked'
		try:
			os.rename(filename, locked_filename)
		except FileNotFoundError:
			return
		except BaseException as e:
			L.exception("Error when locking the file '{}'".format(filename))
			self.Pipeline.set_error(e, None)
			return

		try:
			if filename.endswith(".gz"):
				import gzip
				f = gzip.open(locked_filename, self.mode)

			elif filename.endswith(".bz2"):
				import bz2
				f = bz2.open(locked_filename, self.mode)

			elif filename.endswith(".xz") or filename.endswith(".lzma"):
				import lzma
				f = lzma.open(locked_filename, self.mode)

			else:
				f = open(locked_filename, self.mode, newline=self.newline)

		except:
			self.Pipeline.set_error(ProcessingError("The file '{}' could not be read.".format(filename)), None)
			return

		L.debug("Processing file '{}'".format(filename))

		try:
			await self.read(filename, f)
		except:
			try:
				if self.post == "noop":
					# When we should stop, rename file back to original
					os.rename(locked_filename, filename)
				else:
					# Otherwise rename to ...-failed and continue processing
					os.rename(locked_filename, filename + '-failed')
			except:
				L.exception("Error when finalizing the file '{}'".format(filename))
			raise
		finally:
			f.close()

		L.debug("File '{}' processed {}".format(filename, "succefully"))

		# Finalize
		try:
			if self.post == "delete":
				os.unlink(locked_filename)
			elif self.post == "noop":
				os.rename(locked_filename, filename)
			else:
				os.rename(locked_filename, filename + '-processed')
		except BaseException as e:
			L.exception("Error when finalizing the file '{}'".format(filename))
			self.Pipeline.set_error(e, None)
			return


	@abc.abstractmethod
	async def read(self, filename, f):
		'''
		Override this method to implement your File Source.
		`f` is an opened file object.
		'''
		raise NotImplemented()
