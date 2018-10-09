import logging
import pyarrow as pa
import pyarrow.parquet as pq
import pandas as pd
from bspump.abc.sink import Sink

#

L = logging.getLogger(__file__)

#

class ParquetSink(Sink):

	ConfigDefaults = {
		'chunk_size': 1000,
	}

	def __init__(self, app, pipeline, id=None, config=None):
		super().__init__(app, pipeline, id=id, config=config)
		app.PubSub.subscribe("Application.tick/10!", self.on_tick)
		self.Frames = []
		self.ChunkSize = self.Config['chunk_size']
		self.FileName = self.Config['path']
		self._pq_writer = None

	def on_tick(self):
		self.flush()

	def process(self, context, event):

		df = pd.DataFrame([event])
		self.Frames.append(df)

		if len(self.Frames) >= self.ChunkSize:
			self.flush()

	def flush(self):
		if len(self.Frames) != 0:
			table = pa.Table.from_pandas(pd.concat(self.Frames))
			if self._pq_writer is None:
				self._pq_writer = pq.ParquetWriter(self.FileName, table.schema)
			self._pq_writer.write_table(table=table)
			self.Frames = []

	def rotate(self, new_filename=None):
		'''
			Call this to close the currently open file.
		'''
		if new_filename is not None:
			self.FileName = new_filename
		self.flush()
		del self._pq_writer
		self._pq_writer = None
