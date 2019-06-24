import logging

import asyncio

from .fileabcsource import FileABCSource

#

L = logging.getLogger(__file__)

#


class FileLineSource(FileABCSource):

	ConfigDefaults = {
		"one_breath_lines": 10000,
	}

	def __init__(self, app, pipeline, id=None, config=None):
		super().__init__(app, pipeline, id=id, config=config)

		self.OneBreathLines = self.Config["one_breath_lines"]


	async def read(self, filename, f):
		counter = 0

		for line in f:

			await self.process(line, {
				"filename": filename
			})

			# Give chance to others when we are in the middle of massive processing
			counter += 1
			if counter >= self.OneBreathLines:
				await asyncio.sleep(0.01)
				counter = 0

#


class FileMultiLineSource(FileABCSource):
	'''
	Read file line by line but try to join multi-line events by separator.
	Separator is a (fixed) pattern that should present at the begin of the line, if it is a new event.

	Example:
	<133>1 2018-03-24T02:37:01+00:00 machine program 22068 - Start of the multiline event
	    2nd line of the event
	    3rd line of the event
	<133>1 2018-03-24T02:37:01+00:00 machine program 22068 - New event

	The separatpr is '<' string in this case

	'''

	ConfigDefaults = {
		"one_breath_lines": 10000,
	}

	def __init__(self, app, pipeline, separator, id=None, config=None):
		super().__init__(app, pipeline, id=id, config=config)

		if isinstance(separator, str):
			separator = separator.encode('utf-8')

		self._separator = separator
		#TODO: self._max_latch_size = 10000

		self.OneBreathLines = self.Config["one_breath_lines"]


	async def read(self, filename, f):
		latch = None
		counter = 0

		for line in f:
			if line.startswith(self._separator) and latch is not None:
				await self.process(latch)
				latch = line

			else:
				if latch is None:
					latch = line
				else:
					latch = latch + b'\n' + line

			# Give chance to others when we are in the middle of massive processing
			counter += 1
			if counter >= self.OneBreathLines:
				await asyncio.sleep(0.01)
				counter = 0

		if latch is not None:
			await self.process(latch, {
				"filename": filename
			})

