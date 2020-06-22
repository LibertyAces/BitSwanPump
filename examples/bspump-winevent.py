#!/usr/bin/env python3
import logging

import bspump
import bspump.common
import bspump.winapi

###

L = logging.getLogger(__name__)

###

"""
The following example works only on Windows based systems,
since it uses `bspump.winapi` module.
"""


class WinEventPipeline(bspump.Pipeline):
	"""
	Obtain Windows Events and print them to the terminal.
	"""

	def __init__(self, app, pipeline_id):
		super().__init__(app, pipeline_id)

		self.build(
			bspump.winapi.WinEventSource(app, self, config={
				"server": "localhost",
				"event_type": "System",
			}),
			bspump.common.PPrintSink(app, self),
		)


if __name__ == '__main__':
	app = bspump.BSPumpApplication()

	svc = app.get_service("bspump.PumpService")

	# Construct and register the pipeline
	pl = WinEventPipeline(app, 'WinEventPipeline')
	svc.add_pipeline(pl)

	app.run()
