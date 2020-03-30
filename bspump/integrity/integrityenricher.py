import bspump
import logging
# The library is called pyjwt when installing package via pip (pip install pyjwt)
import jwt


###

L = logging.getLogger(__name__)

###


class IntegrityEnricher(bspump.Processor):

	'''
	IntegrityEnricher is a enricher processor, which enriches JSON data
	by hashed events. Data are encoded by JSON Web Tokens standards.

...

	Supported algorithms for cryptographic signing, default is HS256


	HS256 - HMAC using SHA-256 hash algorithm (default)
	HS384 - HMAC using SHA-384 hash algorithm
	HS512 - HMAC using SHA-512 hash algorithm
	ES256 - ECDSA signature algorithm using SHA-256 hash algorithm
	ES384 - ECDSA signature algorithm using SHA-384 hash algorithm
	ES512 - ECDSA signature algorithm using SHA-512 hash algorithm
	RS256 - RSASSA-PKCS1-v1_5 signature algorithm using SHA-256 hash algorithm
	RS384 - RSASSA-PKCS1-v1_5 signature algorithm using SHA-384 hash algorithm
	RS512 - RSASSA-PKCS1-v1_5 signature algorithm using SHA-512 hash algorithm
	PS256 - RSASSA-PSS signature using SHA-256 and MGF1 padding with SHA-256
	PS384 - RSASSA-PSS signature using SHA-384 and MGF1 padding with SHA-384
	PS512 - RSASSA-PSS signature using SHA-512 and MGF1 padding with SHA-512
	'''

	ConfigDefaults = {
		'key_path': '',
		'algorithm': 'HS256',
		'hash_name': 'hash',
		'prev_hash_name': 'previous_hash',
		'hash_id_name': 'hash_id'
	}


	def __init__(self, app, pipeline, id=None, config=None):
		super().__init__(app, pipeline, id, config)
		self.KeyPath = self.Config['key_path']
		self.Algorithm = self.Config['algorithm']
		self.HashKey = self.Config['hash_name']
		self.PrevHashKey = self.Config['prev_hash_name']
		self.HashIdKey = self.Config['hash_id_name']

		self.PreviousHash = None
		self.HashId = 0

		# Check if the key path is set
		self.JWTPrivateKey = None
		if self.KeyPath == '' or self.KeyPath is None:
			self.JWTPrivateKey = None
		else:
			with open(self.KeyPath, 'r') as file:
				self.JWTPrivateKey = file.read()


	# Encoding event and enriching JSON with the encoded event
	def process(self, context, event):

		# Check on loaded key
		if self.JWTPrivateKey is None:
			L.warning('Key has not been loaded!')
			return

		# Check if hash / previous hash already present in event and if so, delete it from event
		event.pop(self.HashKey, None)
		event.pop(self.PrevHashKey, None)
		event.pop(self.HashIdKey, None)
		# Hash event
		event[self.HashKey] = jwt.encode(event, self.JWTPrivateKey, algorithm=self.Algorithm).decode("utf-8")
		# Set previous hash
		event[self.PrevHashKey] = self.PreviousHash
		# Actuall hash will become previous hash in the next iteration
		self.PreviousHash = event[self.HashKey]
		self.HashId += 1
		# Enrich event by hash ID to faster event comparison in integrity checker
		# Hashed events are sorted by HashId on request to ES from bsintegrity
		# It is a prevention of proceeding comparison on unsorted events. Comparison on
		# unsorted events can produce odd results
		event[self.HashIdKey] = self.HashId
		return event
