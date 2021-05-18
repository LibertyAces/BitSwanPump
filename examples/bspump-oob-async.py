#!/usr/bin/env python3
import logging
import time

import aiohttp

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

	The following example illustrates how to use OOB with long-running asynchronous operations.

	"""

	async def generate(self, context, event, depth):
		# Run asynchronous heavy task
		L.debug("Running long operation asynchronously and waiting for the result...")
		async with aiohttp.ClientSession() as session:
			async with session.get("https://reqres.in/api/{}/2".format(event.get("description", "unknown"))) as resp:
				if resp.status != 200:
					return event
				color = await resp.json()
				event["color_obtained_in_async"] = color
				event["time"] = time.time()

		self.Pipeline.inject(context, event, depth)


class SamplePipeline(bspump.Pipeline):

	def __init__(self, app, pipeline_id):
		super().__init__(app, pipeline_id)

		self.build(
			bspump.http.HTTPClientSource(app, self, config={
				'url': 'https://api.coindesk.com/v1/bpi/currentprice.json'
			}).on(bspump.trigger.PeriodicTrigger(app, 1)),
			bspump.common.BytesToStringParser(app, self),
			bspump.common.StdJsonToDictParser(app, self),
			SampleOOBGenerator(app, self),
			bspump.common.PPrintSink(app, self),
		)


if __name__ == '__main__':
	app = bspump.BSPumpApplication()

	svc = app.get_service("bspump.PumpService")

	sample_pipeline = SamplePipeline(app, 'SamplePipeline')
	svc.add_pipeline(sample_pipeline)

	app.run()
