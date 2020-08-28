import bspump.common
import bspump.unittest
import bspump.trigger


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
		# TODO Generalize to SourceTestCase
		svc = self.App.get_service("bspump.PumpService")

		iterator = iter([1, 2, 3])

		pipeline = bspump.Pipeline(app=self.App)
		sink = bspump.unittest.UnitTestSink(self.App, pipeline)
		source = bspump.common.IteratorSource(self.App, pipeline, iterator).on(
			bspump.trigger.PubSubTrigger(self.App, "Application.run!", self.App.PubSub)
		)
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
