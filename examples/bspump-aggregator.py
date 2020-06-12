#!/usr/bin/env python3
import asyncio
import logging

import bspump
import bspump.common
#
from bspump.common import Aggregator, ListEventAggregationStrategy

L = logging.getLogger(__name__)

#

"""
Example usage of Aggregator pattern
"""


class IntStreamSource(bspump.Source):

	async def main(self):
		event = 0
		while True:
			await asyncio.sleep(1)
			await self.Pipeline.ready()
			await self.Pipeline.process(event)
			event += 1


class AggregatorPipeline(bspump.Pipeline):

	def __init__(self, app, pipeline_id):
		super().__init__(app, pipeline_id)
		self.build(
			IntStreamSource(app, self),
			Aggregator(app, self,
					   aggregation_strategy=ListEventAggregationStrategy(),
					   config={'completion_interval': 5, 'completion_size': 1000}
					   ),
			bspump.common.PPrintSink(app, self)
		)


if __name__ == '__main__':

	app = bspump.BSPumpApplication()

	svc = app.get_service("bspump.PumpService")

	svc.add_pipeline(
		AggregatorPipeline(app, "AggregatorPipeline"),
	)

	app.run()
