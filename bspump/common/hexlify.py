import binascii

from ..abc.processor import Processor


class HexlifyProcessor(Processor):

	def process(self, context, event):
		"""
		Description:

		:return: binascii.hexlify(event)

		|

		"""
		return binascii.hexlify(event)
