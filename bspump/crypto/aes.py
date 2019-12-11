import binascii

from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend

from ..abc.processor import Processor


class CommonAESMixin(object):


	ConfigDefaults = {
		"key": "00000000000000000000000000000000",  # Hexadecimal key, It must be 16 (AES-128), 24 (AES-192), or 32 (AES-256) bytes long.
		"iv": "00000000000000000000000000000000",
	}


	def initalize_aes(self):
		backend = default_backend()

		key = binascii.unhexlify(self.Config['key'])
		iv = binascii.unhexlify(self.Config['iv'])

		self.padding = padding.PKCS7(128)
		self.cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=backend)



class EncryptAESProcessor(Processor, CommonAESMixin):


	def __init__(self, app, pipeline, id=None, config=None):
		super().__init__(app, pipeline, id, config)
		self.initalize_aes()


	def process(self, context, event):
		encryptor = self.cipher.encryptor()
		padder = self.padding.padder()
		data = padder.update(event) + padder.finalize()
		return encryptor.update(data) + encryptor.finalize()


class DecryptAESProcessor(Processor, CommonAESMixin):


	def __init__(self, app, pipeline, id=None, config=None):
		super().__init__(app, pipeline, id, config)
		self.initalize_aes()


	def process(self, context, event):
		decryptor = self.cipher.decryptor()
		unpadder = self.padding.unpadder()
		data = decryptor.update(event) + decryptor.finalize()
		return unpadder.update(data) + unpadder.finalize()
