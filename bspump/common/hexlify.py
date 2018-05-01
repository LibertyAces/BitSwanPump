import binascii

from ..abc.processor import Processor


class HexlifyProcessor(Processor):

	def process(self, context, event):
		return binascii.hexlify(event)
