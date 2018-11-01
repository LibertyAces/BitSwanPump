import os
import hashlib
import json

import aiohttp.web
import asab.web.rest

####

async def pipelines(request):
	app = request.app['app']
	svc = app.get_service("bspump.PumpService")
	return asab.web.rest.json_response(request, svc.Pipelines)


async def example_trigger(request):
	app = request.app['app']
	app.PubSub.publish("mymessage!")
	return asab.web.rest.json_response(request, {'ok': 1})


async def example_internal(request):
	app = request.app['app']
	svc = app.get_service("bspump.PumpService")
	source = svc.locate("SampleInternalPipeline.*InternalSource")
	source.put({"event": "example"})
	return asab.web.rest.json_response(request, {'ok': 1})


async def lookup(request):
	lookup_id = request.match_info.get('lookup_id')
	app = request.app['app']
	svc = app.get_service("bspump.PumpService")
	request_etag = request.headers.get('ETag')

	try:
		lookup = svc.locate_lookup(lookup_id)
	except KeyError:
		raise aiohttp.web.HTTPNotFound()

	try:
		data = lookup.serialize()
	except AttributeError:
		raise aiohttp.web.HTTPNotImplemented()

	assert(isinstance(data, bytes))

	response_etag = hashlib.sha1(data).hexdigest()
	if request_etag == response_etag:
		raise aiohttp.web.HTTPNotModified()

	return aiohttp.web.Response(body=data, status=200,
		headers= {
			'ETag': response_etag
		},
		content_type="application/octet-stream")


def initialize_web(app, listen):
	app.add_module(asab.web.Module)

	websvc = app.get_service("asab.WebService")

	# Create a dedicated web container
	container = asab.web.WebContainer(websvc, 'bspump:web', config={"listen": listen})

	# Add web app
	asab.web.StaticDirProvider(
		container.WebApp,
		root='/',
		path=os.path.join(os.path.dirname(__file__), "static"),
		index="app.html")

	# Add routes
	container.WebApp.router.add_get('/pipelines', pipelines)
	container.WebApp.router.add_get('/example/trigger', example_trigger)
	container.WebApp.router.add_get('/example/internal', example_internal)

	container.WebApp.router.add_get('/lookup/{lookup_id}', lookup)

	return websvc
