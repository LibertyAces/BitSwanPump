import os
import hashlib
import json

import aiohttp.web
import asab.web.rest

####

async def index(request):
	return aiohttp.web.FileResponse(os.path.join(request.app['static_dir'], 'app.html'))


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

	if isinstance(data, dict):
		response_etag = hashlib.sha1(json.dumps(data).encode('utf-8')).hexdigest()
	elif isinstance(data, str):
		response_etag = hashlib.sha1(data.encode('utf-8')).hexdigest()
	else:
		response_etag = hashlib.sha1(data).hexdigest()

	if request_etag == response_etag:
		raise aiohttp.web.HTTPNotModified()

	return asab.web.rest.json_response(request,
		{
			'result': 'OK',
			'data': data,
		},
		headers={
			'ETag': response_etag
		}
	)


def initialize_web(app):
	from asab.web import Module
	app.add_module(Module)

	svc = app.get_service("asab.WebService")

	static_dir = os.path.join(os.path.dirname(__file__), "static")
	svc.WebApp['static_dir'] = static_dir

	svc.WebApp.router.add_get('/', index)
	svc.WebApp.router.add_get('/pipelines', pipelines)
	svc.WebApp.router.add_static('/static/', path=static_dir, name='static')

	svc.WebApp.router.add_get('/example/trigger', example_trigger)
	svc.WebApp.router.add_get('/example/internal', example_internal)

	svc.WebApp.router.add_get('/lookup/{lookup_id}', lookup)

	return svc
