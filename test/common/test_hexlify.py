import bspump.unittest
import bspump.common


class TestHexlifyProcessor(bspump.unittest.ProcessorTestCase):

	def test_hexlify_processor(self):
		events = {
			(None, b'\x124Vx'),
			(None, b'\xab\xba\xba\xbe'),
			(None, b'\xde\xad\xc0\xde'),
		}

		self.set_up_processor(bspump.common.HexlifyProcessor)

		output = self.execute(
			events
		)

		self.assertEqual(
			sorted([event for context, event in output]),
			[b'12345678', b'abbababe', b'deadc0de']
		)
