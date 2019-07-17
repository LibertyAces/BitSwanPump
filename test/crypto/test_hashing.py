import bspump.crypto
import bspump.unittest

# Classes


class SHA256HashingProcessor(bspump.crypto.HashingProcessor):
	ConfigDefaults = {
		"algorithm": "sha256"
	}


class SHA224HashingProcessor(bspump.crypto.HashingProcessor):
	ConfigDefaults = {
		"algorithm": "sha224"
	}


class SHA384HashingProcessor(bspump.crypto.HashingProcessor):
	ConfigDefaults = {
		"algorithm": "sha384"
	}


class SHA512HashingProcessor(bspump.crypto.HashingProcessor):
	ConfigDefaults = {
		"algorithm": "sha512"
	}


class SHA1HashingProcessor(bspump.crypto.HashingProcessor):
	ConfigDefaults = {
		"algorithm": "sha1"
	}


class MD5HashingProcessor(bspump.crypto.HashingProcessor):
	ConfigDefaults = {
		"algorithm": "md5"
	}


class BLAKE2BHashingProcessor(bspump.crypto.HashingProcessor):
	ConfigDefaults = {
		"algorithm": "blake2b"
	}


class BLAKE2SHashingProcessor(bspump.crypto.HashingProcessor):
	ConfigDefaults = {
		"algorithm": "blake2s",
		"digest_size": 32,
	}


class UnknownAlgorithmHashingProcessor(bspump.crypto.HashingProcessor):
	ConfigDefaults = {
		"algorithm": "__unknown__"
	}


class MD5ContextHashingProcessor(bspump.crypto.CoHashingProcessor):
	ConfigDefaults = {
		"algorithm": "md5"
	}

# Test


class TestSHA256HashingProcessor(bspump.unittest.ProcessorTestCase):

	def test_sha256_hashing_processor(self):
		events = [
			(None, b'deadc0de'),
		]

		self.set_up_processor(SHA256HashingProcessor)

		output = self.execute(
			events
		)
		self.assertEqual(len(output[0][1]), 32)
		self.assertEqual(
			output[0][1],
			b'\x86ex\x08\x1a\x1d\xeas\xbeG\xdc\xdeE3K\x17\xb2\xcc\xc0=\x88-\xa2\xd0\xfb\x1eQ\xec\x9d\xdcse'
		)


class TestSHA224HashingProcessor(bspump.unittest.ProcessorTestCase):

	def test_sha224_hashing_processor(self):
		events = [
			(None, b'deadc0de'),
		]

		self.set_up_processor(SHA224HashingProcessor)

		output = self.execute(
			events
		)
		self.assertEqual(len(output[0][1]), 28)
		self.assertEqual(
			output[0][1],
			b"\xfch\xfc\x9e*\x04\x83\x17\x9f\xd7'\xc63w\x9f\xb6\x01\xf2\n~\xa4?J\x84z\xcaCb"
		)


class TestSHA384HashingProcessor(bspump.unittest.ProcessorTestCase):

	def test_sha384_hashing_processor(self):
		events = [
			(None, b'deadc0de'),
		]

		self.set_up_processor(SHA384HashingProcessor)

		output = self.execute(
			events
		)
		self.assertEqual(len(output[0][1]), 48)
		self.assertEqual(
			output[0][1],
			b'\xf4\xee\x1d\x1e)\xaa_\x1dQ#\xcf\xf3\xf7\xfb \xeb\xe4\xca>z\x95\xf4\xddf_q\xd2\x9f\x93\xa7\x98n\xc6?\x92\x16\x8a2\x1b\x14\x7f\xc4e\ra<\xc9\x88'  # noqa
		)


class TestSHA512HashingProcessor(bspump.unittest.ProcessorTestCase):

	def test_sha512_hashing_processor(self):
		events = [
			(None, b'deadc0de'),
		]

		self.set_up_processor(SHA512HashingProcessor)

		output = self.execute(
			events
		)
		self.assertEqual(len(output[0][1]), 64)
		self.assertEqual(
			output[0][1],
			b'9~sN\x11\x0e \xe9-\xca\xd2O\xea\x8d\xdd\xc0t\'^\xb8\xb8VE\xae\xe7\xe5\xa0<\xadc\xd2\x1c\xd3\t(\xb0\x84w\xe9U\x108a\xb3\xa1\xd5\xfb\x02\xdf24"tV\xa7\xa8\xcc\x1e\x7f\x19Aw\x9b\xf2'  # noqa
		)


class TestSHA1HashingProcessor(bspump.unittest.ProcessorTestCase):

	def test_sha1_hashing_processor(self):
		events = [
			(None, b'deadc0de'),
		]

		self.set_up_processor(SHA1HashingProcessor)

		output = self.execute(
			events
		)
		self.assertEqual(len(output[0][1]), 20)
		self.assertEqual(
			output[0][1],
			b'@\x87\x98K\xa8u\xf9\x7f(\xd1\xa8=\x11\x9bcKT\xab\x1e\xe2'
		)


class TestMD5HashingProcessor(bspump.unittest.ProcessorTestCase):

	def test_md5_hashing_processor(self):
		events = [
			(None, b'deadc0de'),
		]

		self.set_up_processor(MD5HashingProcessor)

		output = self.execute(
			events
		)
		self.assertEqual(len(output[0][1]), 16)
		self.assertEqual(
			output[0][1],
			b'\xdb^R\x1f\xe0rP\xeb|o\x01\xda\xd9\xe4#\xfd'
		)


class TestBLAKE2BHashingProcessor(bspump.unittest.ProcessorTestCase):

	def test_blake2b_hashing_processor(self):
		events = [
			(None, b'deadc0de'),
		]

		self.set_up_processor(BLAKE2BHashingProcessor)

		output = self.execute(
			events
		)
		self.assertEqual(len(output[0][1]), 64)
		self.assertEqual(
			output[0][1],
			b'\xe4\x17+\xc0\xf0#\xe4\x99T\x1eM\x11\x08\x82W\x1f%\x9a\xe6\xd5)\xc4\xeb\x8f\xafJqW\xb4_\x92T\x13\x83\xea\x8bb\xf4\n\xf7w\xc0\xd6\xe8\xf1J\xb7\rs\xc1\x02C\xe3L\x96a\x16\xf7\x91\xe6\x84Kb\xba'  # noqa
		)


class TestBLAKE2SHashingProcessor(bspump.unittest.ProcessorTestCase):

	def test_blake2b_hashing_processor(self):
		events = [
			(None, b'deadc0de'),
		]

		self.set_up_processor(BLAKE2SHashingProcessor)

		output = self.execute(
			events
		)
		self.assertEqual(len(output[0][1]), 32)
		self.assertEqual(
			output[0][1],
			b'T\xd5\xda\x91\x80\xae7,/\x94D\\\x82\xaf"*."\xfc\x94\xb0F\xfa\x10\xce<\xcbF\x04\xa5\xe2)'
		)


class TestUnknownAlgorithmHashingProcessor(bspump.unittest.ProcessorTestCase):
	def test_unknown_algorithm_hashing_processor(self):
		with self.assertRaises(RuntimeError):
			self.set_up_processor(UnknownAlgorithmHashingProcessor)

# Context Hashing Test


class TestMD5ContextHashingProcessor(bspump.unittest.ProcessorTestCase):

	def test_md5_hashing_processor(self):
		events = [
			({}, b'deadc0de'),
		]

		self.set_up_processor(MD5ContextHashingProcessor)

		output = self.execute(
			events
		)
		self.assertEqual(len(output[0][0]['hash']), 16)
		self.assertEqual(
			output[0][0]['hash'],
			b'\xdb^R\x1f\xe0rP\xeb|o\x01\xda\xd9\xe4#\xfd'
		)

