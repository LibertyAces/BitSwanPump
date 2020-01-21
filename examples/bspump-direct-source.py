#!/usr/bin/env python3
import asyncio
import logging
import random
import string
import time

import bspump
import bspump.common

#

L = logging.getLogger(__name__)

#

"""
The following example illustrates synchronous processing of an event
passed to a secondary pipeline via a processor located in the primary pipeline. 
"""


class RandomSource(bspump.Source):

	async def main(self):
		while True:
			await asyncio.sleep(0.1)
			await self.Pipeline.ready()
			event = random.choice(''.join(random.choices(string.ascii_uppercase + string.digits, k=32)))
			await self.Pipeline.process(event)


class SecondaryTaskProcessor(bspump.Processor):
	"""
	A router processor that routes events to the secondary pipeline.
	"""

	def __init__(self, app, pipeline, id=None, config=None):
		super().__init__(app, pipeline, id, config)
		self.BSPumpService = self.App.get_service("bspump.PumpService")

	def process(self, context, event):
		direct_source = self.BSPumpService.locate("TargetPipeline.*DirectSource")
		direct_source.put(context, "Event '{}' processed in secondary pipeline.".format(event))
		return "Event '{}' processed in primary pipeline.".format(event)


class RandomSourcePipeline(bspump.Pipeline):

	def __init__(self, app, pipeline_id):
		super().__init__(app, pipeline_id)
		self.build(
			RandomSource(app, self),
			SecondaryTaskProcessor(app, self),
			bspump.common.PPrintSink(app, self)
		)


class SlowProcessor(bspump.Processor):

	def process(self, context, event):
		time.sleep(1)
		return event


class TargetPipeline(bspump.Pipeline):

	def __init__(self, app, pipeline_id):
		super().__init__(app, pipeline_id)
		self.build(
			bspump.common.DirectSource(app, self),
			SlowProcessor(app, self),
			bspump.common.PPrintSink(app, self)
		)


if __name__ == '__main__':

	app = bspump.BSPumpApplication()

	svc = app.get_service("bspump.PumpService")

	svc.add_pipelines(
		TargetPipeline(app, "TargetPipeline"),
		RandomSourcePipeline(app, "RandomSourcePipeline"),
	)

	app.run()
