import aiohttp
import logging
import json
import re
from ..abc.source import TriggerSource

L = logging.getLogger(__name__)


class ElasticSearchSource(TriggerSource):
	"""
	request_body - https://www.elastic.co/guide/en/elasticsearch/reference/current/search-request-body.html

	scroll_timeout - Timeout of single scroll request. Allowed time units:
	https://www.elastic.co/guide/en/elasticsearch/reference/current/common-options.html#time-units
	"""

	ConfigDefaults = {
		'index': 'index-*',
		'scroll_timeout': '1m',

	}

	def __init__(self, app, pipeline, connection, request_body=None, id=None, config=None):
		super().__init__(app, pipeline, id=id, config=config)
		self.Connection = pipeline.locate_connection(app, connection)

		self.Index = self.Config['index']
		self.ScrollTimeout = self.Config['scroll_timeout']

		if request_body is not None:
			self.RequestBody = request_body
		else:
			self.RequestBody = {
				'request_body': {
					'bool': {
						'must': {
							'match_all': {}
						}
					}
				}}

	async def cycle(self):

		scroll_id = None

		while True:
			if scroll_id is None:
				path = self.Index + '/_search?scroll={}'.format(self.ScrollTimeout)
				request_body = self.RequestBody
			else:
				path = "_search/scroll"
				request_body = {"scroll": self.ScrollTimeout, "scroll_id": scroll_id}

			url = self.Connection.get_url() + path
			async with self.Connection.get_session() as session:
				async with session.post(
					url,
					json=request_body,
					headers={'Content-Type': 'application/json'}
				) as response:

					if response.status != 200:
						data = await response.text()
						L.error("Failed to fetch data from ElasticSearch: {} from {}\n{}".format(response.status,url, data))
						break

					msg = await response.json()

			scroll_id = msg.get('_scroll_id')
			if scroll_id is None:
				break

			hits = msg['hits']['hits']
			if len(hits) == 0:
				break

			# Feed messages into a pipeline
			for hit in hits:
				await self.process(hit['_source'])
