#!/usr/bin/env python3
import bspump
import bspump.common
import bspump.http
import bspump.web


class SamplePipeline(bspump.Pipeline):

	def __init__(self, app, pipeline_id):
		super().__init__(app, pipeline_id)

		self.WebServiceSource = bspump.http.WebServiceSource(app, self)
		self.WebServiceSink = bspump.http.WebServiceSink(app, self)

		self.build(
			self.WebServiceSource,
			self.WebServiceSink
		)


	async def webservice(self, request):
		response = await self.WebServiceSink.response(request)
		async with response:
			data = await request.read()
			await self.WebServiceSource.put({self.WebServiceSink.CONTEXT_RESPONSE_ID:response.Id}, data, request)
		return response


if __name__ == '__main__':
	app = bspump.BSPumpApplication()

	svc = app.get_service("bspump.PumpService")

	# Construct and register Pipeline
	pl = SamplePipeline(app, 'SamplePipeline')
	svc.add_pipeline(pl)

	# Locate web service
	app.add_module(bspump.web.Module)
	websvc = app.get_service("asab.WebService")

	websvc.WebApp.router.add_post('/bspump/sp', pl.webservice)

	app.run()
