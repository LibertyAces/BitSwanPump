import binascii

from ..abc.processor import Processor


class HexlifyProcessor(Processor):
	"""
	Description:

	|

	"""

	def process(self, context, event):
		"""
		Description:

		:return: binascii.hexlify(event)

		|

		"""
		return binascii.hexlify(event)
