import binascii
from Crypto.Cipher import AES

from ..abc.processor import Processor
from .padding import PKCS7Padding, NoPadding

#

class CommonAESMixin(object):

	ConfigDefaults = {
		"key" : "00000000000000000000000000000000", # Hexadecimal key, It must be 16 (AES-128), 24 (AES-192), or 32 (AES-256) bytes long.
		"iv": "00000000000000000000000000000000",
		"mode": "CBC", # One of ECB (Electronic Code Book), CBC (Cipher-Block Chaining), CFB (Cipher FeedBack), OFB (Output FeedBack), CTR (CounTer Mode), OPENPGP (OpenPGP Mode)
		"padding": "PKCS7", # One of 'PKCS7', 'None'
	}


	def initalize_aes(self):
		self.Key = binascii.unhexlify(self.Config['key'])
		self.IV = binascii.unhexlify(self.Config['iv'])
		
		self.Mode = {
			'ECB': AES.MODE_ECB,
			'CBC': AES.MODE_CBC,
			'CFB': AES.MODE_CFB,
			'OFB': AES.MODE_OFB,
			'CTR': AES.MODE_CTR,
			'OPENPGP': AES.MODE_OPENPGP,
		}.get(self.Config['mode'].upper())
		if self.Mode is None:
			L.error("Unknown AES mode '{}'".format(self.Config['mode']))
			raise RuntimeError("Unknown AES mode")

		self.Padding = {
			'None': NoPadding,
			'PKCS7': PKCS7Padding,
		}.get(self.Config['padding'].upper())(AES.block_size, self.Config)
		if self.Padding is None:
			L.error("Unknown padding '{}'".format(self.Config['padding']))
			raise RuntimeError("Unknown padding")


	def cipher(self, context):
		'''
		Override this method for a custom AES cipher configuration
		'''
		iv = context.get('iv', self.IV)
		return AES.new(self.Key, self.Mode, iv)

#

class DecryptAESProcessor(Processor, CommonAESMixin):

	def __init__(self, app, pipeline, id=None, config=None):
		super().__init__(app, pipeline, id, config)
		self.initalize_aes()


	def process(self, context, event):
		cipher = self.cipher(context)
		event = cipher.decrypt(event)
		event = self.Padding.decode(event)
		return event

#

class EncryptAESProcessor(Processor, CommonAESMixin):


	def __init__(self, app, pipeline, id=None, config=None):
		super().__init__(app, pipeline, id, config)
		self.initalize_aes()


	def process(self, context, event):
		cipher = self.cipher(context)
		event = self.Padding.encode(event)
		event = cipher.encrypt(event)
		return event
