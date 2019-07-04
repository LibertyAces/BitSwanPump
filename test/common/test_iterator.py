import bspump.unittest
import bspump.common


# TODO TestIteratorSource


class TestIteratorGenerator(bspump.unittest.ProcessorTestCase):

	def test_iterator_generator(self):
		event_message = "Generate me!"
		events = {
			(None, event_message),
		}

		self.set_up_processor(bspump.common.IteratorGenerator)

		output = self.execute(
			events
		)

		self.assertEqual(
			[event for context, event in output],
			[i for i in event_message]
		)
