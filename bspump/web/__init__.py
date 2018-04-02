import os
import aiohttp.web

from .json import json_response

####

async def index(request):
	return aiohttp.web.FileResponse(os.path.join(request.app['static_dir'], 'app.html'))


async def pipelines(request):
	app = request.app['app']
	svc = app.get_service("bspump.PumpService")
	return json_response(request, svc.Pipelines)


def initialize_web(app):
	from module_web import Module
	app.add_module(Module)

	svc = app.get_service("asab.WebService")

	static_dir = os.path.join(os.path.dirname(__file__), "static")
	svc.WebApp['static_dir'] = static_dir

	svc.WebApp.router.add_get('/', index)
	svc.WebApp.router.add_get('/pipelines', pipelines)
	svc.WebApp.router.add_static('/static/', path=static_dir, name='static')

	return svc
