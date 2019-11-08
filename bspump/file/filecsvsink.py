import csv
import logging
from ..abc.sink import Sink
import asyncio
from datetime import datetime
from asab.timer import Timer
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
		'lineterminator': '\r\n',
		'quotechar': '"',
		'quoting': csv.QUOTE_MINIMAL,  # 0 - 3 for [QUOTE_MINIMAL, QUOTE_ALL, QUOTE_NONNUMERIC, QUOTE_NONE]
		'skipinitialspace': False,
		'strict': False,
		'output_queue_max_size': 500,
		'timer': 4,
	}

	def __init__(self, app, pipeline, id=None, config=None):
		super().__init__(app, pipeline, id=id, config=config)
		self.Dialect = csv.get_dialect(self.Config['dialect'])
		self._csv_writer = None
		self._output_queue_max_size = int(self.Config.get('output_queue_max_size'))
		assert (self._output_queue_max_size >= 1), "Output queue max size invalid"
		self._conn_future = None
		self._output_queue = asyncio.Queue()
#		app.PubSub.subscribe("Application.tick!", self.write_to_file)
		self.num = 0
		self.FlushPeriod = int(self.Config.get("timer"))
		self.AnalyzeTimer = Timer(app, self.write_to_file, autorestart=True)
		self.AnalyzeTimer.start(self.FlushPeriod)

	def get_file_name(self, context, event):
		'''
		Override this method to gain control over output file name.
		'''
		return self.Config['path']


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

		return csv.DictWriter(f,
			dialect=self.Dialect,
			fieldnames=fieldnames,
			**kwargs
		)

	async def write_to_file(self):
		# Looping through asyncio queue
		while True:
			# Each time we get context and item out
			context, item = await self._output_queue.get()
			# As long as we have no writer yet, we make one and write header rows
			if self._csv_writer is None:
				# Open CSV file if needed, name the file using current time (maybe slow)
				fieldnames = item.keys()
				fname = str(datetime.now().time()).replace(":", "_").replace(".", "_") + ".csv"
				fo = open(fname, 'w', newline='')
				self._csv_writer = self.writer(fo, fieldnames)
				self._csv_writer.writeheader()
				print("saving..")
			# Now we have headers and _csv_writer, we take each item comming out of the asyncio
			# queue (which represents a row of data) and write it inside of the new .csv
			self._csv_writer.writerow(item)
			self._output_queue.task_done()
			# Once we empty the asyncio queue, we call the rotate method, that deletes
			# our writer and breaks the loop
			if self._output_queue.qsize() == 0:
				self.rotate()
				print("break.")
				break


	# Inside of the process we fill up the asyncio queue and monitor its max size to apply
	# trottling if needed
	def process(self, context, event: [dict, list]):
		if self._output_queue.qsize() >= self._output_queue_max_size:
			self.Pipeline.throttle(self, True)

		self._output_queue.put_nowait([context, event])


	def rotate(self):
		'''
		Call this to close the currently open file.
		'''
		del self._csv_writer
		self._csv_writer = None
