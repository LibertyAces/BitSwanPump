import bspump
import jwt
import aiohttp
import asyncio
import logging
import json


###

L = logging.getLogger(__name__)

###


class IntegrityCheckerProcessor(bspump.Processor):

	ConfigDefaults = {
		'index': 'index-*',
		'key_path': '',
		'algorithm': 'HS256',
		'items_size': "50",
	}

	def __init__(self, app, pipeline, connection, id=None, config=None):
		super().__init__(app, pipeline, id, config)
		self.Connection = pipeline.locate_connection(app, connection)
		self.Index = self.Config['index']
		self.ItemsSize = self.Config['items_size']

		self.KeyPath = self.Config['key_path']
		self.Algorithm = self.Config['algorithm']


	async def request_es(self):
		while True:
			path = '{}/_search?scroll=1m&size={}'.format(self.Index, self.ItemsSize)
			url = self.Connection.get_url() + path
			async with self.Connection.get_session() as session:
				async with session.post(
					url,
					json={
						# "size": self.ItemsSize, TODO
						'query': {
							'bool': {
								'must': {
									'match_all': {}
								}
							}
						}},
					headers={'Content-Type': 'application/json'}
				) as response:

					if response.status != 200:
						data = await response.text()
						L.error("Failed to fetch data from ElasticSearch: {} from {}\n{}".format(response.status, url, data))
						break

					msg = await response.json()

			hits = msg['hits']['hits']
			if len(hits) == 0:
				break


			# TODO 
			# Feed messages into a pipeline
			# for hit in hits:
			# 	await self.process(hit['_source'])

