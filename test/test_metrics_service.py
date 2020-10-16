import bspump.common
from bspump import Processor, Pipeline
from bspump.trigger import PubSubTrigger
from bspump.unittest import UnitTestSource, UnitTestSink


class RaisingProcessor(Processor):

    def process(self, context, event):
        if "warning" in event or "error" in event:
            raise Exception()
        return event


class WarningPipeline(Pipeline):

    def __init__(self, app, id=None, config=None):

        super().__init__(app, id, config)
        self.PubSub.subscribe("bspump.pipeline.cycle_end!", self._on_finished)
        self.Source = UnitTestSource(app, self).on(
            PubSubTrigger(app, "Application.run!", app.PubSub)
        )
        self.Processor = RaisingProcessor(app, self)
        self.Sink = UnitTestSink(app, self)
        self.build(
            self.Source,
            self.Processor,
            self.Sink
        )

    def handle_error(self, exception, context, event):
        if event == "warning":
            return True
        return not super().handle_error(exception, context, event)

    def _on_finished(self, event_name, pipeline):
        self.App.stop()


class TestMetricsService(bspump.unittest.ProcessorTestCase):

    def _metric_flush(self, _, __, counter):
        if counter.get("error"):
            self.ErrorCount += counter["error"]
        if counter.get("warning"):
            self.WarningCount += counter["warning"]

    def test_metrics_service(self):
        self.ErrorCount = 0
        self.WarningCount = 0

        self.App.PubSub.subscribe(
            "Application.Metrics.Flush!",
            self._metric_flush
        )

        svc = self.App.get_service("bspump.PumpService")

        self.Pipeline = WarningPipeline(self.App)

        self.Pipeline.Source.Input = [
            (None, "ok"),
            (None, "warning"),
            (None, "error"),
        ]
        self.Pipeline.PubSub.publish("unittest.go!")
        svc.add_pipeline(self.Pipeline)
        self.App.run()

        self.assertEqual(
            [({}, "ok")],
            self.Pipeline.Sink.Output
        )
        self.assertEqual(2, self.WarningCount)
        self.assertEqual(0, self.ErrorCount)
