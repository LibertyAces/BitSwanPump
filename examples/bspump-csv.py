#!/usr/bin/env python3
import logging

import bspump
import bspump.common
import bspump.file
import bspump.trigger

###

L = logging.getLogger(__name__)


###


class SamplePipeline(bspump.Pipeline):

	def __init__(self, app, pipeline_id):
		super().__init__(app, pipeline_id)

		self.Sink = bspump.file.FileCSVSink(app, self, config={'path': './data/out.csv'})

		self.build(
			bspump.file.FileCSVSource(
				app, self, config={'path': './data/sample.csv', 'delimiter': ';', 'post': 'noop'}
			).on(bspump.trigger.RunOnceTrigger(app)),
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
	import string, random

	svc.add_pipeline(pl)
	contexts = []
	length = 10
	for i in range(length):
		letters = string.ascii_letters
		name = ''.join((random.choice(letters) for j in range(length)))
		contexts.append({'tenant': name})
	for i in range(length*2):
		context = random.choice(contexts)
		try:
			res = 1 / 0
		except Exception as e:
			pl.set_error(context, None, e)
			init_values = {
				'event.in': 1,
				'event.out': 1,
				'event.drop': 1,
				'warning': 1,
				'error': 1,
			}
			for key, value in init_values.items():
				_event = (key, value)
				pl.add_events_to_counters(_event)
	# _do_process(None
	app.run()
