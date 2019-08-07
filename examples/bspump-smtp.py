#!/usr/bin/env python3
import logging

import bspump
import bspump.common
import bspump.common
import bspump.file
import bspump.mail
import bspump.trigger

###

L = logging.getLogger(__name__)

###


class SamplePipeline(bspump.Pipeline):
	"""

	## Try it out

		$ python -m smtpd -c DebuggingServer -n localhost:1025

	"""

	def __init__(self, app, pipeline_id):
		super().__init__(app, pipeline_id)

		self.build(

			bspump.file.FileLineSource(app, self, 'FileLineSource1', config={
				'path': './data/hello.txt',
				'post': 'noop',
			}).on(bspump.trigger.RunOnceTrigger(app)),

			bspump.common.BytesToStringParser(app, self),
			bspump.common.PPrintProcessor(app, self),
			bspump.mail.SmtpSink(app, self, 'SmtpConnection')
		)


if __name__ == '__main__':
	app = bspump.BSPumpApplication()

	svc = app.get_service("bspump.PumpService")

	svc.add_connection(
		bspump.mail.SmtpConnection(app, "SmtpConnection", config={
			"server": "localhost",
			"port": 1025,
			"from": "my@email.com",
			"to": "your@email.com,his@email.com",
			"cc": "her@email.com",
			"bcc": "its@email.com",
			"subject": "BSPump mailing service",
			"output_queue_max_size": 10
		})
	)

	# Construct and register Pipeline
	pl = SamplePipeline(app, 'SamplePipeline')
	svc.add_pipeline(pl)

	app.run()
