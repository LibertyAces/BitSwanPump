import logging

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes

from ..abc.processor import Processor

#

L = logging.getLogger(__name__)

#


class HashingBaseProcessor(Processor):

	ConfigDefaults = {
		"algorithm": "sha256",
		"digest_size": 64,
	}


	def __init__(self, app, pipeline, id=None, config=None):
		super().__init__(app, pipeline, id, config)

		self.Backend = default_backend()

		algorithm = self.Config['algorithm'].upper()

		if algorithm == "SHA224":
			self.Algorithm = hashes.SHA224()
		elif algorithm == "SHA256":
			self.Algorithm = hashes.SHA256()
		elif algorithm == "SHA384":
			self.Algorithm = hashes.SHA384()
		elif algorithm == "SHA512":
			self.Algorithm = hashes.SHA512()
		elif algorithm == "SHA1":
			self.Algorithm = hashes.SHA1()
		elif algorithm == "MD5":
			self.Algorithm = hashes.MD5()
		elif algorithm == "BLAKE2B":
			digest_size = int(self.Config['digest_size'])
			self.Algorithm = hashes.BLAKE2b(digest_size)
		elif algorithm == "BLAKE2S":
			digest_size = int(self.Config['digest_size'])
			self.Algorithm = hashes.BLAKE2s(digest_size)
		else:
			L.error("Unknown hashing algorithm '{}'".format(self.Config['algorithm']))
			raise RuntimeError("Unknown hashing algorithm '{}'".format(self.Config['algorithm']))



class HashingProcessor(HashingBaseProcessor):

	'''
	Create hash of the event.
	'''

	def process(self, context, event):
		digest = hashes.Hash(self.Algorithm, self.Backend)
		digest.update(event)
		return digest.finalize()


class CoHashingProcessor(HashingBaseProcessor):

	'''
	Put hash of the event into a context.
	'''

	def process(self, context, event):
		digest = hashes.Hash(self.Algorithm, self.Backend)
		digest.update(event)
		context['hash'] = digest.finalize()
		return event
