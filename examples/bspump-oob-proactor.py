#!/usr/bin/env python3
import logging

import requests
import time

import asab
import asab.proactor
import bspump
import bspump.common
import bspump.http
import bspump.trigger

###

L = logging.getLogger(__name__)

###


class SampleOOBGenerator(bspump.Generator):
	"""
	Generator processes originally synchronous events "out-of-band" e.g. out of the synchronous
	processing within the pipeline.

	Specific implementation of Generator should implement the generate method to process events
	while performing long running (asynchronous) tasks such as HTTP requests.
	The long running tasks may enrich events with relevant information, such as output of external calculations.

	The following example illustrates how to use OOB with long-running synchronous operations running on threads,
	using the ASAB Proactor module.

	"""

	def __init__(self, app, pipeline, id=None, config=None):
		super().__init__(app, pipeline, id=id, config=config)

		app.add_module(asab.proactor.Module)
		self.ProactorService = app.get_service("asab.ProactorService")

	async def generate(self, context, event, depth):
		# Run synchronous heavy task on thread
		L.debug("Running long operation on thread and waiting for the result...")
		new_event = await self.ProactorService.execute(
			self.process_on_thread,
			context,
			event
		)

		await self.Pipeline.inject(context, new_event, depth)

	def process_on_thread(self, context, event):
		r = requests.get("https://reqres.in/api/{}/4".format(event.get("description", "unknown")))
		event["color_obtained_via_proactor"] = r.json()
		event["time"] = time.time()
		return event


class SamplePipeline(bspump.Pipeline):

	def __init__(self, app, pipeline_id):
		super().__init__(app, pipeline_id)

		self.build(
			bspump.http.HTTPClientSource(app, self, config={
				'url': 'https://api.coindesk.com/v1/bpi/currentprice.json'
			}).on(bspump.trigger.PeriodicTrigger(app, 1)),
			bspump.common.BytesToStringParser(app, self),
			bspump.common.JsonToDictParser(app, self),
			SampleOOBGenerator(app, self),
			bspump.common.PPrintSink(app, self),
		)


if __name__ == '__main__':
	app = bspump.BSPumpApplication()

	svc = app.get_service("bspump.PumpService")

	sample_pipeline = SamplePipeline(app, 'SamplePipeline')
	svc.add_pipeline(sample_pipeline)

	app.run()
