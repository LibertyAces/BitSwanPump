import csv
import logging
from ..abc.sink import Sink

#

L = logging.getLogger(__file__)

#

class FileCSVSink(Sink):

	ConfigDefaults = {
		'path': '',
		'dialect': 'excel',
		'delimiter': None,
		'doublequote': None,
		'escapechar': None,
		'lineterminator': None,
		'quotechar': None,
		'quoting': None,
		'skipinitialspace': None,
		'strict': None,
	}

	def __init__(self, app, pipeline, id=None, config=None):
		super().__init__(app, pipeline, id=id, config=config)
		self.Dialect = csv.get_dialect(self.Config['dialect'])
		self._csv_writer = None


	def get_file_name(self, context, event):
		'''
		Override this method to gain control over output file name.
		'''
		return self.Config['path']


	def writer(self, f, fieldnames):
		kwargs = {}

		v = self.Config.get('delimiter')
		if v is not None: kwargs['delimiter'] = v

		v = self.Config.get('doublequote')
		if v is not None: kwargs['doublequote'] = v

		v = self.Config.get('escapechar')
		if v is not None: kwargs['escapechar'] = v

		v = self.Config.get('lineterminator')
		if v is not None: kwargs['lineterminator'] = v

		v = self.Config.get('quotechar')
		if v is not None: kwargs['quotechar'] = v

		v = self.Config.get('quoting')
		if v is not None: kwargs['quoting'] = v

		v = self.Config.get('skipinitialspace')
		if v is not None: kwargs['skipinitialspace'] = v

		v = self.Config.get('strict')
		if v is not None: kwargs['strict'] = v

		return csv.DictWriter(f,
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
