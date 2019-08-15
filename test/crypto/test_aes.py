import bspump.crypto
import bspump.unittest


class CommonAESConfig(object):
	ConfigDefaults = {
		"key": "FD49F6AD21E24F36E51F7B49C37B1A97",
		"iv": "99C07A9AE2AA16486A21E504ECE4377D",
	}


class CustomEncryptAESProcessor(bspump.crypto.EncryptAESProcessor, CommonAESConfig):
	pass


class CustomDecryptAESProcessor(bspump.crypto.DecryptAESProcessor, CommonAESConfig):
	pass


class TestEncryptAESProcessor(bspump.unittest.ProcessorTestCase):

	def test_encrypt_aes_processor(self):
		events = [
			(None, b'deadc0de'),
		]

		self.set_up_processor(CustomEncryptAESProcessor)

		output = self.execute(
			events
		)
		self.assertEqual(len(output[0][1]), 16)
		self.assertEqual(
			output[0][1],
			b'3\xeaj\xb6\xc4S\xc2\x8a\xef]\xf6\xfc\t\xc1\xd2\x02'
		)


class TestDecryptAESProcessor(bspump.unittest.ProcessorTestCase):

	def test_encrypt_aes_processor(self):
		events = [
			(None, b'3\xeaj\xb6\xc4S\xc2\x8a\xef]\xf6\xfc\t\xc1\xd2\x02'),
		]

		self.set_up_processor(CustomDecryptAESProcessor)

		output = self.execute(
			events
		)

		self.assertEqual(
			output[0][1],
			b'deadc0de'
		)
