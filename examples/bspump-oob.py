#!/usr/bin/env python3
import logging
import requests

import aiohttp

import bspump
import bspump.http
import bspump.common
import bspump.trigger
import bspump.oob

import asab
import asab.proactor

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

	def __init__(self, app, destination):
		super().__init__(app, destination)

		app.add_module(asab.proactor.Module)
		self.ProactorService = app.get_service("asab.ProactorService")

	async def process(self, context, event):
		# Run asynchronous heavy task
		L.debug("Running long operation asynchronously and waiting for the result...")
		async with aiohttp.ClientSession() as session:
			async with session.get("https://reqres.in/api/{}/2".format(event.get("description", "unknown"))) as resp:
				if resp.status != 200:
					return event
				color = await resp.json()
				event["color"] = color

		# Run synchronous heavy task on thread
		L.debug("Running long operation on thread and waiting for the result...")
		event = await self.ProactorService.execute(
			self.process_on_thread,
			context,
			event
		)

		return event

	def process_on_thread(self, context, event):
		r = requests.get("https://reqres.in/api/{}/4".format(event.get("description", "unknown")))
		event["second_color"] = r.json()
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
