#!/usr/bin/env python3
import aiohttp.web
import asab
import asab.web
import bspump
import bspump.common
import bspump.http


class SamplePipeline(bspump.Pipeline):

	def __init__(self, app, pipeline_id):
		super().__init__(app, pipeline_id)

		self.build(
			bspump.http.WebServiceSource(app, self),
			bspump.http.WebServiceSink(app, self)
		)


class WebAdapter(object):


	def __init__(self, app):
		svc = app.get_service("bspump.PumpService")
		self.WebServiceSource = svc.locate('SamplePipeline.*WebServiceSource')
		self.WebServiceSink = svc.locate('SamplePipeline.WebServiceSink')


	async def endpoint(self, request):
		response = await self.WebServiceSink.response(request)
		async with response:
			data = await request.read()
			await self.WebServiceSource.put({self.WebServiceSink.CONTEXT_RESPONSE_ID:response.Id}, data, request)
		return response


if __name__ == '__main__':
	app = bspump.BSPumpApplication(web=True)

	svc = app.get_service("bspump.PumpService")

	# Construct and register Pipeline
	pl = SamplePipeline(app, 'SamplePipeline')
	svc.add_pipeline(pl)

	# Locate web service
	websvc = app.get_service("asab.WebService")

	# Construct web adapter
	wa = WebAdapter(app)

	websvc.WebApp.router.add_post('/bspump/sp', wa.endpoint)

	app.run()
