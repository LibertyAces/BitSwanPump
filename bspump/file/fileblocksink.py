import logging
from ..abc.sink import Sink

#

L = logging.getLogger(__file__)

#

class FileBlockSink(Sink):

	ConfigDefaults = {
		'path': '',
	}


	def get_file_name(self, context, event):
		'''
		Override this method to gain control over output file name.
		'''
		return self.Config['path']


	def process(self, context, event):
		fname = self.get_file_name(context, event)
		with open(fname, 'wb') as fo:
			fo.write(event)
