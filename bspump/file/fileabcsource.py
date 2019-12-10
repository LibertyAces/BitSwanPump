import abc
import asyncio
import logging
import os

import time

from .globscan import _glob_scan
from ..abc.source import TriggerSource


L = logging.getLogger(__file__)


class FileABCSource(TriggerSource):


	ConfigDefaults = {
		'path': '',
		'mode': 'rb',
		'newline': os.linesep,
		'post': 'move',  # one of 'delete', 'noop' and 'move'
		'exclude': '',  # glob of filenames that should be excluded (has precedence over 'include')
		'include': '',  # glob of filenames that should be included
		'encoding': '',
		'move_destination': '',  # destination folder for 'move'. Make sure it's outside of the glob search
		'lines_per_event': 10000,  # the number of lines after which the read method enters the idle state to allow other operations to perform their tasks
		'event_idle_time': 0.01,  # the time for which the read method enters the idle state (see above)
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
		conf_encoding = self.Config['encoding']
		self.encoding = conf_encoding if len(conf_encoding) > 0 else None

		self.MoveDestination = self.Config['move_destination']

		if (self.MoveDestination != ''):
			if (self.post == 'move') and (not os.path.isdir(self.MoveDestination)):
				os.makedirs(self.MoveDestination)
		else:
			self.MoveDestination = None

		metrics_service = app.get_service('asab.MetricsService')
		self.Gauge = metrics_service.create_gauge(
			"file_count",
			tags={
				'pipeline': pipeline.Id,
			},
			init_values={
				"processed": 0,
				"failed": 0,
				"locked": 0,
				"unprocessed": 0,
				"all_files": 0,
				"scan_time": 0.0,
			}
		)

		self.Loop = app.Loop

		self.LinesCounter = 0
		self.LinesPerEvent = int(self.Config["lines_per_event"])
		self.EventIdleTime = float(self.Config["event_idle_time"])

	async def cycle(self):
		filename = None

		start_time = time.time()
		for path in self.path.split(os.pathsep):
			filename = _glob_scan(path, self.Gauge, self.Loop, exclude=self.exclude, include=self.include)
			if filename is not None:
				break
		end_time = time.time()
		self.Gauge.set("scan_time", end_time - start_time)

		if filename is None:
			self.Pipeline.PubSub.publish("bspump.file_source.no_files!")
			return  # No file to read

		await self.Pipeline.ready()

		# Lock the file
		L.debug("Locking file '{}'".format(filename))
		locked_filename = filename + '-locked'
		try:
			os.rename(filename, locked_filename)
		except FileNotFoundError:
			return
		except (OSError, PermissionError):  # OSError - UNIX, PermissionError - Windows
			L.exception("Error when locking the file '{}'  - will try again".format(filename))
			return
		except BaseException as e:
			L.exception("Error when locking the file '{}'".format(filename))
			self.Pipeline.set_error(None, None, e)
			return

		try:
			if filename.endswith(".gz"):
				import gzip
				f = gzip.open(locked_filename, self.mode, encoding=self.encoding)

			elif filename.endswith(".bz2"):
				import bz2
				f = bz2.open(locked_filename, self.mode, encoding=self.encoding)

			elif filename.endswith(".xz") or filename.endswith(".lzma"):
				import lzma
				f = lzma.open(locked_filename, self.mode, encoding=self.encoding)

			else:
				if 'b' in self.mode:  # Binary mode doesn't take a newline argument
					self.newline = None
				f = open(locked_filename, self.mode, newline=self.newline, encoding=self.encoding)

		except (OSError, PermissionError):  # OSError - UNIX, PermissionError - Windows
			L.exception("Error when opening the file '{}' - will try again".format(filename))
			return
		except BaseException as e:
			L.exception("Error when opening the file '{}'".format(filename))
			self.Pipeline.set_error(None, None, e)
			return

		L.debug("Processing file '{}'".format(filename))

		try:
			await self.read(filename, f)
		except Exception:
			try:
				if self.post == "noop":
					# When we should stop, rename file back to original
					os.rename(locked_filename, filename)
				else:
					# Otherwise rename to ...-failed and continue processing
					os.rename(locked_filename, filename + '-failed')
			except BaseException:
				L.exception("Error when renaming the file '{}'  - will try again".format(filename))
			return
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
				if self.MoveDestination is not None:
					file_from = os.path.abspath(locked_filename)
					base = os.path.basename(filename)
					file_to = os.path.abspath(os.path.join(self.MoveDestination, base + '-processed'))
				else:
					file_from = locked_filename
					file_to = filename + "-processed"

				os.rename(file_from, file_to)
		except (OSError, PermissionError):  # OSError - UNIX, PermissionError - Windows
			L.exception("Error when finalizing the file '{}' - will try again".format(filename))
			return
		except BaseException as e:
			L.exception("Error when finalizing the file '{}'".format(filename))
			self.Pipeline.set_error(None, None, e)
			return

	async def simulate_event(self):
		'''
		The simulate_event method should be called in read method after a file line has been processed.

		It ensures that all other asynchronous events receive enough time to perform their tasks.
		Otherwise, the application loop is blocked by a file reader and no other activity makes a progress.
		'''

		self.LinesCounter += 1
		if self.LinesCounter >= self.LinesPerEvent:
			await asyncio.sleep(self.EventIdleTime)
			self.LinesCounter = 0

	@abc.abstractmethod
	async def read(self, filename, f):
		'''
		Override this method to implement your File Source.
		`f` is an opened file object.
		'''
		raise NotImplementedError()
