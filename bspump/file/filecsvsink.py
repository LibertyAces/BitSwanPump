import csv
import logging
import os

from ..abc.sink import Sink

#

L = logging.getLogger(__file__)


#

class FileCSVSink(Sink):
	ConfigDefaults = {
		'path': '',
		'dialect': 'excel',
		'delimiter': ',',
		'doublequote': True,
		'escapechar': "",
		'lineterminator': os.linesep,
		'quotechar': '"',
		'quoting': csv.QUOTE_MINIMAL,  # 0 - 3 for [QUOTE_MINIMAL, QUOTE_ALL, QUOTE_NONNUMERIC, QUOTE_NONE]
		'skipinitialspace': False,
		'strict': False,
	}

	def __init__(self, app, pipeline, id=None, config=None):
		super().__init__(app, pipeline, id=id, config=config)
		self.Dialect = csv.get_dialect(self.Config['dialect'])
		self._csv_writer = None

	def get_file_name(self, context, event):
		'''
		Override this method to gain control over output file name.
		'''
		# Here we are able to modify the sink behavior from outside using context.
		# If provided, the filename (and path) is taken from the context instead of the config
		return context.get("path", self.Config["path"])

	def writer(self, f, fieldnames):
		kwargs = dict()

		kwargs['delimiter'] = self.Config.get('delimiter')
		kwargs['doublequote'] = bool(self.Config.get('doublequote'))

		escape_char = self.Config.get('escapechar')
		escape_char = None if escape_char == "" else escape_char
		kwargs['escapechar'] = escape_char

		kwargs['lineterminator'] = self.Config.get('lineterminator')
		kwargs['quotechar'] = self.Config.get('quotechar')
		kwargs['quoting'] = int(self.Config.get('quoting'))
		kwargs['skipinitialspace'] = bool(self.Config.get('skipinitialspace'))
		kwargs['strict'] = bool(self.Config.get('strict'))

		return csv.DictWriter(
			f,
			dialect=self.Dialect,
			fieldnames=fieldnames,
			**kwargs
		)

	def process(self, context, event):
		if self._csv_writer is None:
			# Open CSV file if needed
			fieldnames = event.keys()
			fname = self.get_file_name(context, event)
			fo = open(fname, 'w', newline='')
			self._csv_writer = self.writer(fo, fieldnames)
			self._csv_writer.writeheader()

		self._csv_writer.writerow(event)

	def rotate(self):
		'''
		Call this to close the currently open file.
		'''
		del self._csv_writer
		self._csv_writer = None
