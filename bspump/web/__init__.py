import datetime
import hashlib
import os
import os.path
import logging

import aiohttp.web

import asab
import asab.web.rest
from asab.web.auth import noauth

from ..__version__ import __build__ as bspump_build
from ..__version__ import __version__ as bspump_version

#

L = logging.getLogger(__name__)

#


@noauth
async def pipelines(request):
	app = request.app['app']
	svc = app.get_service("bspump.PumpService")
	return asab.web.rest.json_response(request, svc.Pipelines)


@noauth
async def example_trigger(request):
	app = request.app['app']
	app.PubSub.publish("mymessage!")
	return asab.web.rest.json_response(request, {'ok': 1})


@noauth
async def example_internal(request):
	app = request.app['app']
	svc = app.get_service("bspump.PumpService")
	source = svc.locate("SampleInternalPipeline.*InternalSource")
	source.put({"event": "example"})
	return asab.web.rest.json_response(request, {'ok': 1})


@noauth
async def lookup_list(request):
	app = request.app['app']
	svc = app.get_service("bspump.PumpService")
	return asab.web.rest.json_response(request, [lookup.rest_get() for lookup in svc.Lookups.values()])


@noauth
async def lookup_meta(request):
	lookup_id = request.match_info.get('lookup_id')
	app = request.app['app']
	svc = app.get_service("bspump.PumpService")
	try:
		lookup = svc.locate_lookup(lookup_id)
	except KeyError:
		raise aiohttp.web.HTTPNotFound()
	return asab.web.rest.json_response(request, lookup.rest_get())


@noauth
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

	assert isinstance(data, bytes)

	response_etag = hashlib.sha1(data).hexdigest()
	if (request_etag is not None) and (request_etag == response_etag):
		raise aiohttp.web.HTTPNotModified()

	return aiohttp.web.Response(
		body=data, status=200,
		headers={
			'ETag': response_etag
		},
		content_type="application/octet-stream")


@noauth
async def manifest(request):
	'''
	$ curl http://localhost:8080/manifest?pretty=true
	{
		"ASAB_VERSION": "18.12b1",
		"DOCKER_HOST": "${DOCKER_HOST}",
		"BSPUMP_VERSION": "1.2.3",
		"APP_VERSION": "1.2.3",
		"MANIFEST_MTIME": "2019-01-29T21:54:15.780668"
	}

	Served from `/manifest` file.
	The format of the file is:
KEY1=VALUE
KEY2=${ENVIRONMENT_VARIABLE}
	'''

	app = request.app['app']

	d = {
		'ASAB_VERSION': asab.__version__,
		'BSPUMP_VERSION': bspump_version,
		'BSPUMP_BUILD': bspump_build,
		'LAUNCHED_AT': datetime.datetime.utcfromtimestamp(app.LaunchTime).isoformat(),
	}

	container_host = os.environ.get('CONTAINER_HOST')
	if container_host is not None:
		d['CONTAINER_HOST'] = container_host

	try:

		fname = '/manifest'
		mtime = os.path.getmtime(fname)
		with open(fname) as f:
			for line in f:
				k, v = line.strip().split('=', 1)
				if k not in d:
					d[k] = os.path.expandvars(v)
		d['MANIFEST_MTIME'] = datetime.datetime.utcfromtimestamp(mtime).isoformat()
	except FileNotFoundError:
		pass
	return asab.web.rest.json_response(request, d)


def initialize_web(container):

	# Add routes

	# API VERSION 1
	container.WebApp.router.add_get('/bspump/v1/pipelines', pipelines)
	container.WebApp.router.add_get('/bspump/v1/example/trigger', example_trigger)
	container.WebApp.router.add_get('/bspump/v1/example/internal', example_internal)

	container.WebApp.router.add_get('/bspump/v1/lookup', lookup_list)
	container.WebApp.router.add_get('/bspump/v1/lookup/{lookup_id}', lookup)
	container.WebApp.router.add_get('/bspump/v1/lookup/{lookup_id}/meta', lookup_meta)

	container.WebApp.router.add_get('/bspump/v1/manifest', manifest)

	return container
