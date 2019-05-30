#!/usr/bin/env python3
import logging

import aiohttp

import bspump
import bspump.http
import bspump.common
import bspump.trigger
import bspump.oob


###

L = logging.getLogger(__name__)

###


class SampleOOBEngine(bspump.oob.OOBEEngine):
	"""
	OOBEngine allows you to perform long synchronous operations "out-of-band" e.g. out of the synchronous processing within the pipeline.

	The following diagram illustrates the architecture of the "out-of-band" module with OOBESink and OOBEEngine:

	PipelineA (synchronous)
	+---+---+---+---+---+---+
	Source	Processors	OOBESink
	+---+---+---+---+---+---+
							|
					SampleOOBEngine (asynchronous)
							|
							PipelineB (synchronous)
							+---+---+---+---+---+---+---+
							InternalSource  Processors  Sink
							+---+---+---+---+---+---+---+
	"""

	async def process(self, context, event):

		async with aiohttp.ClientSession() as session:

			async with session.get("https://reqres.in/api/{}/2".format(event.get("description", "unknown"))) as resp:
				if resp.status != 200:
					return event
				color = await resp.json()
				event["color"] = color

		return event


class PipelineA(bspump.Pipeline):

	def __init__(self, app, pipeline_id):
		super().__init__(app, pipeline_id)

		svc = app.get_service("bspump.PumpService")
		engine = SampleOOBEngine(app, svc.locate("PipelineB.*InternalSource"))

		self.build(
			bspump.http.HTTPClientSource(
				app,
				self,
				config={
					'url': 'https://api.coindesk.com/v1/bpi/currentprice.json'
				}
			).on(bspump.trigger.PeriodicTrigger(app, 1)),
			bspump.common.BytesToStringParser(app, self),
			bspump.common.JsonToDictParser(app, self),
			bspump.oob.OOBESink(app, self, engine),
		)


class PipelineB(bspump.Pipeline):

	def __init__(self, app, pipeline_id):
		super().__init__(app, pipeline_id)

		self.build(
			bspump.common.InternalSource(app, self),
			bspump.common.PPrintSink(app, self),
		)


if __name__ == '__main__':
	app = bspump.BSPumpApplication()

	svc = app.get_service("bspump.PumpService")

	# Register pipelines in the exact order

	pipeline_b = PipelineB(app, 'PipelineB')
	svc.add_pipeline(pipeline_b)

	pipeline_a = PipelineA(app, 'PipelineA')
	svc.add_pipeline(pipeline_a)

	app.run()
