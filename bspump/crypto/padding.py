import sys
from ..abc.processor import Processor

#

class NoPadding(object):
	'''
	The risk connected with NoPadding is that the data will not be aligned with block size expectation of the cipher, hence encrypt operation will fail.
	'''

	def __init__(self, block_size, config):
		pass

	def encode(self, data):
		return data

	def decode(self, data):
		return data

#

class PKCS7Padding(object):


	def __init__(self, block_size, config):
		assert(block_size > 0)
		assert(block_size < 256) # PKCS7 padding is not defined above 255

		self.BlockSize = block_size
		self.Validate = True


	def encode(self, data):
		data_len = len(data)

		padding_len = self.BlockSize - (data_len % self.BlockSize)
		assert(padding_len > 0)
		assert(padding_len <= self.BlockSize)

		padding = (padding_len).to_bytes(1, byteorder=sys.byteorder) * padding_len
		return data + padding


	def decode(self, data):
		padding_len = data[-1]
		assert(padding_len > 0)
		assert(padding_len <= self.BlockSize)

		if self.Validate:
			for i in range(-padding_len, -1):
				assert(data[i] == padding_len)

		return data[0:-padding_len]
