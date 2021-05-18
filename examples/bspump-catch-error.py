#!/usr/bin/env python3

import json

import bspump
import bspump.common

###


class FailingPipeline(bspump.Pipeline):

	def __init__(self, app, pipeline_id):
		super().__init__(app, pipeline_id)

		self.build(
			bspump.common.InternalSource(app, self),
			bspump.common.StdJsonToDictParser(app, self),
			bspump.common.NullSink(app, self)
		)


	def catch_error(self, exception, event):
		if isinstance(exception, json.decoder.JSONDecodeError):
			print("'{}: {}' is ignored".format(type(exception), exception))
			return False
		return True


if __name__ == '__main__':
	app = bspump.BSPumpApplication()

	svc = app.get_service("bspump.PumpService")

	# Construct and register Pipeline
	pl = FailingPipeline(app, 'SamplePipeline')
	svc.add_pipeline(pl)

	source = pl.locate_source("InternalSource")
	source.put({}, b"Invalid JSON")

	app.run()
