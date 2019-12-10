import os
import logging
from ..abc.sink import Sink


L = logging.getLogger(__file__)


class FileBlockSink(Sink):

	ConfigDefaults = {
		'path': '',
		'mode': "wb",
		'flags': "O_CREAT",
	}

	OFlagDict = {
		'O_CREAT': os.O_CREAT,
		'O_EXCL': os.O_EXCL
	}


	def __init__(self, app, pipeline, id=None, config=None):
		super().__init__(app, pipeline, id=id, config=config)

		self._oflags = 0
		for flag in self.Config["flags"].split(","):
			flag = flag.strip()
			try:
				self._oflags |= self.OFlagDict[flag]
			except KeyError:
				L.warning("Unknown oflag '{}'".format(flag))


	def get_file_name(self, context, event):
		'''
		Override this method to gain control over output file name.
		'''
		return self.Config['path']


	def process(self, context, event):
		fname = self.get_file_name(context, event)

		fd = os.open(fname, os.O_WRONLY | self._oflags)
		with os.fdopen(fd, self.Config['mode']) as fo:
			fo.write(event)
