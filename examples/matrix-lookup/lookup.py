import bspump
import bspump.lookup
import time
import numpy as np
import logging

##

L = logging.getLogger(__name__)

##

class MyMatrixLookup(bspump.lookup.MatrixLookup):
	def __init__(self, app, matrix_id=None, dtype='float_', on_clock_update=False, id=None, config=None, lazy=False):
		super().__init__(app, matrix_id=matrix_id, dtype=dtype, on_clock_update=on_clock_update, id=id, config=config, lazy=lazy)
		self.create_index(bspump.lookup.BitMapIndex, 'channelid', self.Matrix, "ChannelBitMapIndex")
		#self.create_index(bspump.lookup.TreeRangeIndex, 'time_start', 'time_end', self.Matrix, "TimeTreeRangeIndex")
		self.create_index(bspump.lookup.SliceIndex, 'ts_start', 'ts_end', self.Matrix, resolution=30*60, id="TimeSliceIndex")


	async def load(self):
		return True


	def search(self, event):
		# start = time.time()
		# set_timestamp = self.Indexes['TimeTreeRangeIndex'].search(event['@timestamp'])
		set_timestamp = self.Indexes['TimeSliceIndex'].search(event['@timestamp'])
		if len(set_timestamp) == 0:
			return None

		# e = time.time()
		set_channel = self.Indexes['ChannelBitMapIndex'].search(event['channel'])
		if len(set_channel) == 0:
			return None
		# ee = time.time()
		try:
			intersect = list(set_timestamp & set_channel)[0]
		except Exception:
			return None

		b = self.Matrix.Array['programname'][intersect]
		# end = time.time()
		# print()
		return b





