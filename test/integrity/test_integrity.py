import bspump.unittest
from bspump.integrity import IntegrityEnricher


class TestIntegrityEnricher(bspump.unittest.ProcessorTestCase):


	def test_integrity_enricher_01(self):
		events = [
			(None, {
				'number': 124,
				'string': "foo bar",
				'bytes': b"bar foo",
			}),
		]

		self.set_up_processor(IntegrityEnricher)

		output = self.execute(
			events
		)

		print(output)

		# self.assertEqual(len(output[0][1]), 32)
		# self.assertEqual(
		# 	output[0][1],
		# 	b'\x86ex\x08\x1a\x1d\xeas\xbeG\xdc\xdeE3K\x17\xb2\xcc\xc0=\x88-\xa2\xd0\xfb\x1eQ\xec\x9d\xdcse'
		# )


	def test_integrity_enricher_02(self):
		events = [
			(None, {
				'number': 124,
				'string': "foo bar",
				'bytes': b"bar foo",
				'key\u011b': 'value\u011b',
			}),
		]

		self.set_up_processor(IntegrityEnricher)

		output = self.execute(
			events
		)

		print(output)

		# self.assertEqual(len(output[0][1]), 32)
		# self.assertEqual(
		# 	output[0][1],
		# 	b'\x86ex\x08\x1a\x1d\xeas\xbeG\xdc\xdeE3K\x17\xb2\xcc\xc0=\x88-\xa2\xd0\xfb\x1eQ\xec\x9d\xdcse'
		# )
