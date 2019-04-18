#!/usr/bin/env python3
import logging
import asyncio
import asab
import bspump
import bspump.file
import bspump.common
import bspump.mail
import bspump.trigger
import bspump.common

###

L = logging.getLogger(__name__)

###


# python -m smtpd -c DebuggingServer -n localhost:1025


smtp_connection_config = {
	"smtp_server": "localhost",
	"port": 1025,
	"use_tls": False,
	"use_start_tls": False,
	# login:"",
	# password:"",

	"from": "my@email.com",
	"to": "your@email.com,his@email.com",
	"cc": "her@email.com",
	"bcc": "its@email.com",

	"output_queue_max_size": 10,

	"subject": "SMTPSink Test mail"
}

class SamplePipeline(bspump.Pipeline):

	def __init__(self, app, pipeline_id):
		super().__init__(app, pipeline_id)

		self.build(
			bspump.file.FileLineSource(app, self, config={'path': 'data.txt', 'post':'noop'}).on(bspump.trigger.RunOnceTrigger(app)),
			bspump.common.BytesToStringParser (app, self),
			bspump.common.PPrintProcessor(app, self),
			bspump.mail.SmtpSink(app, self, 'SmptConnection')
		)


if __name__ == '__main__':
	app = bspump.BSPumpApplication()

	svc = app.get_service("bspump.PumpService")

	svc.add_connection(
		bspump.mail.SmtpConnection(app, "SmptConnection", config = smtp_connection_config)
	)

	# Construct and register Pipeline
	pl = SamplePipeline(app, 'SamplePipeline')
	svc.add_pipeline(pl)

	app.run()
