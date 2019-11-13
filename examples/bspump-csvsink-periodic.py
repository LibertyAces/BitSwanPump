#!/usr/bin/env python3
import logging

import bspump
import bspump.http
import bspump.common
import bspump.file
import bspump.trigger
import time

###

L = logging.getLogger(__name__)


###

# Periodicity is achieved via means not related to the sink itself, for example through a processor
class TimingProcessor(bspump.Processor):
	def __init__(self, app, pipeline, id=None, config=None):
		super().__init__(app, pipeline, id, config)

	def process(self, context, event):
		time.sleep(1)
		context["path"] = str(self.time()).replace(".", "_") + ".csv"
		return event

class SamplePipeline(bspump.Pipeline):

	def __init__(self, app, pipeline_id):
		super().__init__(app, pipeline_id)
		# By way of not providing the sink with 'filename.csv',
		# the desired behavior is triggered. We may still provide path to store our files
		self.Sink = bspump.file.FileCSVSink(app, self)

		self.build(
			bspump.http.HTTPClientSource(app, self, config={
				'url': "http://ip.jsontest.com/"
			}).on(bspump.trigger.PeriodicTrigger(app, 5)),
			bspump.common.JsonBytesToDictParser(app, self),
			TimingProcessor(app, self),
			bspump.common.PPrintProcessor(app, self),
			self.Sink
		)

		self.PubSub.subscribe("bspump.pipeline.cycle_end!", self.on_cycle_end)

	def on_cycle_end(self, event_name, pipeline):
		'''
		This ensures that at the end of the file scan, the target file is closed
		'''
		self.Sink.rotate()


if __name__ == '__main__':
	app = bspump.BSPumpApplication()

	svc = app.get_service("bspump.PumpService")

	# Construct and register Pipeline
	pl = SamplePipeline(app, 'SamplePipeline')
	svc.add_pipeline(pl)

	app.run()
