#!/usr/bin/env python3
import logging
import time
import bspump
import bspump.avro
import bspump.common
import bspump.file
import bspump.trigger
import asab
###

L = logging.getLogger(__name__)

###

class PerfSink(bspump.Sink):


	def __init__(self, app, pipeline, id=None, config=None):
		super().__init__(app, pipeline, id=id, config=config)

		self.Counter = 0
		self.Mark = time.time()

		app.PubSub.subscribe_all(self)


	def process(self, context, event):
		self.Counter += 1


	@asab.subscribe("Application.tick!")
	def _on_tick(self, event_name):
		now = time.time()

		print("EPS: {:.0f}".format(self.Counter / (now - self.Mark)))

		self.Counter = 0
		self.Mark = now


class SamplePipeline(bspump.Pipeline):

	def __init__(self, app, pipeline_id):
		super().__init__(app, pipeline_id)

		self.build(
			bspump.avro.AvroSource(app, self, config={'path': './data/sink.avro'}).on(bspump.trigger.PeriodicTrigger(app,1)),
			PerfSink(app, self)
		)

	def on_cycle_end(self, event_name, pipeline):
		'''
		This ensures that at the end of the file scan, the target file is closed
		'''


if __name__ == '__main__':
	app = bspump.BSPumpApplication()

	svc = app.get_service("bspump.PumpService")

	# Construct and register Pipeline
	pl = SamplePipeline(app, 'SamplePipeline')
	svc.add_pipeline(pl)

	app.run()
