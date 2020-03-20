import bspump
import logging
# The library is called pyjwt when installing package via pip (pip install pyjwt)
import jwt


###

L = logging.getLogger(__name__)

###


class IntegrityEnricherProcessor(bspump.Processor):

	'''
	IntegrityEnricherProcessor is a enricher processor, which enriches JSON data
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
	}


	def __init__(self, app, pipeline, id=None, config=None):
		super().__init__(app, pipeline, id, config)
		self.KeyPath = self.Config['key_path']
		self.Algorithm = self.Config['algorithm']

		# Check if the key path is set
		self.JWTPrivateKey = None
		if self.KeyPath == '' or self.KeyPath is None:
			self.JWTPrivateKey = None
		else:
			with open(self.KeyPath, 'r') as file:
				self.JWTPrivateKey = file.read()

	# Encoding event and enriching JSON with the encoded event
	def hash_event(self, context, event):
		# Check on loaded key
		if self.JWTPrivateKey is None:
			L.warning('Key has not been loaded!')
			return

		# Check if previous hash present in JSON and if so, delete it
		event.pop("hash", None)
		# Hash event
		event["hash"] = jwt.encode(event, self.JWTPrivateKey, algorithm=self.Algorithm).decode("utf-8")


	def process(self, context, event):
		self.hash_event(context, event)
		return event
