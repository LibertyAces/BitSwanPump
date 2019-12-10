import logging

from .fileabcsource import FileABCSource

#

L = logging.getLogger(__file__)

#


class FileLineSource(FileABCSource):

	def __init__(self, app, pipeline, id=None, config=None):
		super().__init__(app, pipeline, id=id, config=config)


	async def read(self, filename, f):

		for line in f:

			await self.process(line, {
				"filename": filename
			})

			await self.simulate_event()

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

	def __init__(self, app, pipeline, separator, id=None, config=None):
		super().__init__(app, pipeline, id=id, config=config)

		if isinstance(separator, str):
			separator = separator.encode('utf-8')

		self._separator = separator
		# TODO: self._max_latch_size = 10000


	async def read(self, filename, f):
		latch = None

		for line in f:
			if line.startswith(self._separator) and latch is not None:
				await self.process(latch)
				latch = line

			else:
				if latch is None:
					latch = line
				else:
					latch = latch + b'\n' + line

		await self.simulate_event()

		if latch is not None:
			await self.process(latch, {
				"filename": filename
			})
