import bspump
import bspump.lookup
import logging

##

L = logging.getLogger(__name__)

##

class MyMatrixLookup(bspump.lookup.MatrixLookup):
	def __init__(self, app, matrix_id=None, dtype='float_', on_clock_update=False, id=None, config=None, lazy=False):
		super().__init__(app, matrix_id=matrix_id, dtype=dtype, on_clock_update=on_clock_update, id=id, config=config, lazy=lazy)
		self.create_index(bspump.lookup.BitMapIndex, 'channelid', self.Matrix, "ChannelBitMapIndex")

	async def load(self):
		
		return True


