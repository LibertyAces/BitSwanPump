from bspump.unittest import UnitTestSink
from bspump.common import IteratorSource
from bspump import Pipeline

import bspump.unittest
import bspump.common


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


class TestIteratorSource(bspump.unittest.ProcessorTestCase):

	def test_iterator_source(self):
		svc = self.App.get_service("bspump.PumpService")

		iterator = iter([1, 2, 3])

		pipeline = Pipeline(app=self.App)
		sink = UnitTestSink(self.App, pipeline)
		source = IteratorSource(self.App, pipeline, iterator)
		pipeline.build(
			source,
			sink
		)

		pipeline.PubSub.subscribe("bspump.pipeline.cycle_end!", self._on_finished)

		svc.add_pipeline(pipeline)
		source.TriggerEvent.set()
		self.App.run()

		self.assertEqual([({}, 1), ({}, 2), ({}, 3)], sink.Output)

	def _on_finished(self, event_name, pipeline):
		self.App.stop()
