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

	## Try it out

		xxxxxxxxxxxxxxxxxxxxxxx

	"""

	def __init__(self, app, pipeline_id=None):
		super().__init__(app, pipeline_id)

		self.build(
            # bspump.random.RandomSource(app, self, choice=['a', 'b', 'c'], config={
            #     'number': 5
            # }).on(bspump.trigger.OpportunisticTrigger(app, chilldown_period=5)),
			# bspump.common.BytesToStringParser(app, self),
			bspump.ftp.FtpSource(app, self, "FtpConnection", config={'folder_name': '/pub/example/readme.txt'}),
			bspump.common.PPrintSink(app, self),
			# bspump.mail.SmtpSink(app, self, 'SmtpConnection')
		)


if __name__ == '__main__':
	app = bspump.BSPumpApplication()

	svc = app.get_service("bspump.PumpService")

	svc.add_connection(
		bspump.ftp.FtpConnection(app, "FtpConnection")
	)

	# Construct and register Pipeline
	pl = SamplePipeline(app, 'SamplePipeline')
	svc.add_pipeline(pl)

	app.run()