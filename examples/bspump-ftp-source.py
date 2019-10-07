#!/usr/bin/env python3
import logging

import bspump
import bspump.common
import bspump.common
import bspump.file
import bspump.random
import bspump.trigger
import bspump.ftp



###

L = logging.getLogger(__name__)

###


class SamplePipeline(bspump.Pipeline):
	"""
		xxxxxxxxxxxxxxxxxxxxxxx

	"""

	def __init__(self, app, pipeline_id=None):
		super().__init__(app, pipeline_id)

		self.build(
			bspump.ftp.FTPSource(app, self, "FTPConnection", config={'remote_path': '/pub/example/readme.txt',
																	 'local_path': None}),
			bspump.common.PPrintSink(app, self),
			# bspump.mail.SmtpSink(app, self, 'SmtpConnection')
		)


if __name__ == '__main__':
	app = bspump.BSPumpApplication()

	svc = app.get_service("bspump.PumpService")

	svc.add_connection(
		bspump.ftp.FTPConnection(app, "FTPConnection")
	)

	# Construct and register Pipeline
	pl = SamplePipeline(app, 'SamplePipeline')
	svc.add_pipeline(pl)

	app.run()