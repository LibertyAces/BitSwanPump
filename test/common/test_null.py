import bspump.unittest
import bspump.common


class TestNullSink(bspump.unittest.ProcessorTestCase):

	def test_null(self):
		events = [
			(None, "Don't let this out!"),
		]

		self.set_up_processor(bspump.common.NullSink)

		output = self.execute(
			events
		)

		self.assertEqual(
			[event for context, event in output],
			[]
		)
