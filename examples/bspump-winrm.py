#!/usr/bin/env python3
import logging

import bspump
import bspump.common
import bspump.trigger
import bspump.winrm

###

L = logging.getLogger(__name__)

###


class WinRMPipeline(bspump.Pipeline):
	"""
	Periodically performs command to an external Windows system.
	"""

	def __init__(self, app, pipeline_id):
		super().__init__(app, pipeline_id)

		self.build(
			bspump.winrm.WinRMSource(app, self, "WinRMSource", config={
				"endpoint": "http://localhost:5985/wsman",
				"username": "MyDomain\MyUser",
				"password": "MyPassword",
				"command": "ping google.com",
			}).on(bspump.trigger.OpportunisticTrigger(app, chilldown_period=1)),
			bspump.common.PPrintSink(app, self),
		)


if __name__ == '__main__':
	app = bspump.BSPumpApplication()

	svc = app.get_service("bspump.PumpService")

	# Construct and register the pipeline
	pl = WinRMPipeline(app, 'WinRMPipeline')
	svc.add_pipeline(pl)

	app.run()
