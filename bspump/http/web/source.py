import logging

from ...abc.source import Source

#

L = logging.getLogger(__name__)

#


class WebServiceSource(Source):
	'''
This source is to be integrated into aiohttp.web as a 'View'.

Example:
	async def view(self, request):
		await self.WebServiceSource.put(None, data, request)
		return aiohttp.web.Response(text='OK')

	'''

	async def put(self, context, data, request):
		if context is None:
			context = {}

		# Prepare context variables
		context['webservicesource.remote'] = request.remote
		context['webservicesource.path'] = request.path
		context['webservicesource.query'] = request.query
		context['webservicesource.headers'] = request.headers
		context['webservicesource.secure'] = request.secure
		context['webservicesource.method'] = request.method
		context['webservicesource.url'] = request.url
		context['webservicesource.scheme'] = request.scheme
		context['webservicesource.forwarded'] = request.forwarded
		context['webservicesource.host'] = request.host
		context['webservicesource.cookies'] = request.cookies
		context['webservicesource.content_type'] = request.content_type
		context['webservicesource.charset'] = request.charset

		await self.Pipeline.ready()
		await self.process(data, context)


	async def main(self):
		pass
