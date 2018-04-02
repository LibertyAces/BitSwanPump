#!/usr/bin/env python3
import asyncio
import json
import asab
import bspump
import bspump.file
import bspump.socket
import bspump.common
import bspump.http
import bspump.trigger


class SamplePipeline(bspump.Pipeline):

	def __init__(self, app, pipeline_id, trigger):
		super().__init__(app, pipeline_id)

		self.build(
			[
				#bspump.file.FileLineSource(app, self, config={'path': './services'}),
				#bspump.socket.TCPStreamSource(app, self, config={'port': 7000}),
				bspump.http.HTTPClientSource(app, self).trigger(trigger)
			],
			#bspump.common.JSONParserProcessor(app, self),
			bspump.common.TeeProcessor(app, self, "SampleInternalPipeline.*TeeSource"),
			bspump.common.PPrintSink(app, self)
		)

	def catch_error(self, exception, event):
		if isinstance(exception, json.decoder.JSONDecodeError):
			return False
		return True


class SampleInternalPipeline(bspump.Pipeline):

	def __init__(self, app, pipeline_id):
		super().__init__(app, pipeline_id)

		self.build(
			[
				bspump.common.TeeSource(app, self),
			],
			#bspump.common.JSONParserProcessor(app, self),
			bspump.common.PPrintSink(app, self)
		)

	def catch_error(self, exception, event):
		if isinstance(exception, json.decoder.JSONDecodeError):
			return False
		return True



if __name__ == '__main__':
	app = bspump.BSPumpApplication(web=True)
	svc = app.get_service("bspump.PumpService")

	# Construct timer trigger
	ptrg = bspump.trigger.PubSubTrigger(app, "mymessage!")
	

	# Construct and register Pipeline
	pl = SamplePipeline(app, 'SamplePipeline', ptrg)
	svc.add_pipeline(pl)

	# Construct and register Pipeline
	pl = SampleInternalPipeline(app, 'SampleInternalPipeline')
	svc.add_pipeline(pl)

	app.run()
