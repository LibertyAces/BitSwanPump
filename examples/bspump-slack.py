#!/usr/bin/env python3
import logging

import bspump
import bspump.common
import bspump.file
import bspump.slack
import bspump.trigger

###

L = logging.getLogger(__name__)

###


class SamplePipeline(bspump.Pipeline):

	def __init__(self, app, pipeline_id):
		super().__init__(app, pipeline_id)

		self.build(
			bspump.file.FileJSONSource(app, self, config={
				'path': './data/sample.json',
				'post': 'noop',
			}).on(bspump.trigger.RunOnceTrigger(app)),
			bspump.slack.SlackTextSink(app, self, 'SlackConnection')
		)


if __name__ == '__main__':
	app = bspump.BSPumpApplication()

	svc = app.get_service("bspump.PumpService")

	svc.add_connection(
		bspump.slack.SlackConnection(app, "SlackConnection", config={
			# Grab hook_url at https://slack.com/apps/manage
			'hook_url': 'https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXXXXXXXXXX',
		})
	)

	# Construct and register Pipeline
	pl = SamplePipeline(app, 'SamplePipeline')
	svc.add_pipeline(pl)

	app.run()
