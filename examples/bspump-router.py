#!/usr/bin/env python3
import asyncio
import logging
import random
import string

import asab
import asab.web.rest
import bspump
import bspump.common

#

L = logging.getLogger(__name__)

#


class RandomSource(bspump.Source):

	async def main(self):
		while True:
			await asyncio.sleep(0.1)
			await self.Pipeline.ready()
			event = random.choice(['A', 'B', 'C']) + ''.join(random.choices(string.ascii_uppercase + string.digits, k=32))
			await self.Pipeline.process(event)


class CustomRouterSink(bspump.common.RouterSink):
	""" A router sink that routes events based on their type to the type-specific pipelines. """

	TYPE_TO_SOURCE = {
		"A": 	"TargetPipelineA.*SlowerInternalSource",
		"B": 	"TargetPipelineB.*SlowerInternalSource",
		"C": 	"TargetPipelineC.*SlowerInternalSource",
	}


	def process(self, context, event):
		target = self.TYPE_TO_SOURCE.get(event[0], 'A')
		self.route(context, event, target)


class RandomSourcePipeline(bspump.Pipeline):

	def __init__(self, app, pipeline_id):
		super().__init__(app, pipeline_id)
		self.build(
			RandomSource(app, self),
			bspump.common.TeeProcessor(app, self),
			CustomRouterSink(app, self)
		)


class CircuitBreakerError(Exception):
	pass


class CircuitBreaker(bspump.Processor):

	"""
	https://en.wikipedia.org/wiki/Circuit_breaker_design_pattern
	"""

	def __init__(self, app, pipeline, id=None, config=None):
		super().__init__(app, pipeline, id=id, config=config)
		self.State = True


	def set(self, value=False):
		if value == self.State: return

		if value:
			L.info("Circuit breaker '{}' in a pipeline '{}' is on.".format(
				self.Id,
				self.Pipeline.Id,
			))
			
		else:
			L.warning("Circuit breaker '{}' in a pipeline '{}' is OFF.".format(
				self.Id,
				self.Pipeline.Id,
			))

		self.State = value

	def process(self, context, event):
		if not self.State:
			raise CircuitBreakerError("Circuit breaker '{}' in a pipeline '{}' is off.".format(
				self.Id,
				self.Pipeline.Id,
			))
		return event


	def rest_get(self):
		rest = super().rest_get()
		rest['State'] = self.State
		return rest


class SlowerInternalSource(bspump.common.InternalSource):

	async def process(self, event, context=None):
		await asyncio.sleep(0.5)
		await super().process(event, context=None)


class TargetPipeline(bspump.Pipeline):

	def __init__(self, app, pipeline_id):
		super().__init__(app, pipeline_id)
		self.build(
			SlowerInternalSource(app, self),
			CircuitBreaker(app, self),
			bspump.common.PPrintSink(app, self)
		)


class TeePipeline(bspump.Pipeline):

	def __init__(self, app, pipeline_id):
		super().__init__(app, pipeline_id)

		self.build(
			bspump.common.TeeSource(app, self).bind("RandomSourcePipeline.TeeProcessor"),
			bspump.common.PPrintSink(app, self)
		)


async def simulate_fail(request):
	app = request.app['app']
	svc = app.get_service("bspump.PumpService")

	fail = request.query.getone('v', 't') != 't'

	cb = svc.locate("TargetPipelineC.CircuitBreaker")
	cb.set(value=fail)

	return asab.web.rest.json_response(request, data={'OK': True}, pretty=True)


if __name__ == '__main__':
	asab.Config.read_string('''
[asab:web]
listen=127.0.0.1 8080
	''')

	app = bspump.BSPumpApplication()

	svc = app.get_service("bspump.PumpService")

	svc.add_pipelines(
		RandomSourcePipeline(app, "RandomSourcePipeline"),
		TargetPipeline(app, "TargetPipelineA"),
		TargetPipeline(app, "TargetPipelineB"),
		TargetPipeline(app, "TargetPipelineC"),
	)

	svc.add_pipeline(
		TeePipeline(app, "TeePipeline")
	)

	app.add_module(asab.web.Module)
	svc = app.get_service("asab.WebService")
	svc.WebApp.router.add_get('/fail', simulate_fail)

	app.run()
