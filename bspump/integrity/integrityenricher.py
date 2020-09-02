import logging

import secrets
import hashlib
import base64

import orjson

from ..abc.processor import Processor

###

L = logging.getLogger(__name__)

###


class IntegrityEnricher(Processor):
	"""
	IntegrityEnricher is a enricher processor, which enriches JSON data
	by hashed events.

	Supported algorithms for cryptographic signing, default is SHA256
	'SHA256', 'dsaEncryption', 'MD4', 'sha256', 'sha3_512', 'DSA', 'sha3_256', 'sha3_384', 'SHA512', 'md5', 'SHA224',
	'MD5', 'sha', 'whirlpool', 'ripemd160', 'SHA384', 'ecdsa-with-SHA1', 'RIPEMD160', 'sha1', 'blake2s', 'shake_128',
	'blake2b', 'sha512', 'sha224', 'md4', 'SHA', 'dsaWithSHA', 'sha384', 'sha3_224', 'shake_256', 'DSA-SHA', 'SHA1'
	"""

	ConfigDefaults = {
		'algorithm': 'SHA256',
		'hash_key': '_id',
		'prev_hash_key': '_prev_id',
		'salt_length': 3,
	}

	def __init__(self, app, pipeline, id=None, config=None):
		super().__init__(app, pipeline, id, config)
		self.Algorithm = self.Config['algorithm']
		self.HashKey = self.Config['hash_key']
		self.PrevHashKey = self.Config['prev_hash_key']
		self.SaltLength = int(self.Config['salt_length'])
		self.PreviousHash = None

	def process(self, context, event):

		# Check that the event is a dictionary
		assert isinstance(event, dict)

		# Check if hash / previous hash already present in event and if so, delete it from event
		event.pop(self.HashKey, None)

		# Salt event - to ensure that events are not going to be the same after hash
		event["_s"] = secrets.token_urlsafe(self.SaltLength)

		# Set previous hash
		if self.PreviousHash is not None:
			event[self.PrevHashKey] = self.PreviousHash
		else:
			event.pop(self.PrevHashKey, None)

		# Hash event using key, value, key, value ... sequence
		h = hashlib.new(self.Algorithm)
		h.update(orjson.dumps(
			event,
			default=orjson_default,
			option=orjson.OPT_NON_STR_KEYS | orjson.OPT_SORT_KEYS)
		)
		hash_base64 = h.hexdigest()

		# Store the hash as base64 string
		event[self.HashKey] = hash_base64

		# Actual hash will become previous hash in the next iteration
		self.PreviousHash = hash_base64

		return event


def orjson_default(obj):
	if isinstance(obj, bytes):
		return base64.b64encode(obj).decode('ascii')
	raise TypeError
