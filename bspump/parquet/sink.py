import logging
import os
import pyarrow as pa
import pyarrow.parquet as pq
import pandas as pd
from bspump.abc.sink import Sink

#

L = logging.getLogger(__file__)

#

class ParquetSink(Sink):

	ConfigDefaults = {
		'rows_in_chunk': 1000,
		'rollover_mechanism': 'rows',
		'rows_per_file': 10000,
		'file_name_template': './sink{index}.parquet',
	}

	def __init__(self, app, pipeline, id=None, config=None):
		super().__init__(app, pipeline, id=id, config=config)
		app.PubSub.subscribe("Application.tick/10!", self.on_tick)
		self.Frames = []
		self.ChunkSize = self.Config['rows_in_chunk']
		self.RolloverMechanism = self.Config['rollover_mechanism']
		self.FileNameTemplate = self.Config['file_name_template']

		if self.RolloverMechanism == 'rows':

			if self.Config['rows_per_file'] % self.ChunkSize != 0:
				self.ChunksPerFile = int(round(self.Config['rows_per_file'] / self.ChunkSize))
				L.warning('rows_per_file % rows_in_chunk needs to be zero. rows_per_file was rounded')
			elif self.Config['rows_per_file'] < self.ChunkSize:
				self.ChunksPerFile = 1
				L.warning('rows_per_file needs to be equal or greater than rows_in_chunk, rows_per_file changed to rows_in_chunk value')
			else:
				self.ChunksPerFile = int(self.Config['rows_per_file'] / self.ChunkSize)
			self.Chunks = 0
			self.Index = 0

		else:
			self.Index = None
			self.Chunks = None

		self._pq_writer = None


	def build_filename(self, postfix=''):
		return self.FileNameTemplate.format(
			index=('{:04d}'.format(self.Index)) if self.Index is not None else ''
		) + postfix

	def on_tick(self, event_name):
		self.flush()

	def process(self, context, event):

		df = pd.DataFrame([event])
		self.Frames.append(df)

		if len(self.Frames) >= self.ChunkSize:

			if self.RolloverMechanism == 'rows':
				self.Chunks = self.Chunks + 1
				if self.Chunks >= self.ChunksPerFile:
					self.rotate()

			self.flush()

	def flush(self):
		if len(self.Frames) != 0:
			table = pa.Table.from_pandas(pd.concat(self.Frames))
			if self._pq_writer is None:
				self._pq_writer = pq.ParquetWriter(self.build_filename('-open'), table.schema)
			self._pq_writer.write_table(table=table)
			self.Frames = []

	def rotate(self, new_filename=None):
		'''
			Call this to close the currently open file.
		'''

		self.flush()
		del self._pq_writer
		self._pq_writer = None

		current_fname = self.build_filename('-open')
		os.rename(current_fname, current_fname[:-5])

		if self.RolloverMechanism == 'rows':
			self.Index = self.Index + 1
