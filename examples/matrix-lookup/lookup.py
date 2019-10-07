import bspump
import bspump.lookup
import logging

##

L = logging.getLogger(__name__)

##

class MyMatrixLookup(bspump.lookup.MatrixLookup):

	async def load(self):
		self.add_bitmap_index('channelid', id="ChannelBitMapIndex")
		return True


