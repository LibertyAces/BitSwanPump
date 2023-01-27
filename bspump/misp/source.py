import logging
import asab
import requests



###

L = logging.getLogger(__name__)

###



class MISPSource(TriggerSource):
	"""
	Fetches lookup data from given zookeeper URL.
	"""

	def __init__(self, lookup, url, id=None, config=None):
		super().__init__(lookup, url, id, config)
		self.MispUrl = self.Config['url']
		self.AuthToken = self.Config['auth_token']

	async def fetch_feed(self):
		headers = {
			'Authorization': self.AuthToken,
			'Accept': 'application/json',
			'Content-Type': 'application/json',
		}
		# setup get feed-misp-url
		feed_url = "http://" + self.MispUrl + "/feeds/view/" + self.FeedId

		async with session.get(
				feed_url,
				headers=headers
		) as response:

			if response.status != 200:
				data = await response.text()
				L.error("Failed to fetch Feed {} from {}\n{}".format(response.status, url, data))

			return await response.json()

	async def fetch_feeds(self):
		headers = {
			'Authorization': self.AuthToken,
			'Accept': 'application/json',
			'Content-Type': 'application/json',
		}

		feed_url = "http://" + self.MispUrl + "/feeds"
		async with session.get(
				feed_url,
				headers=headers
		) as response:

			if response.status != 200:
				data = await response.text()
				L.error("Failed to fetch Feed {} from {}\n{}".format(response.status, url, data))

			return await response.json()

	async def add_feeds(self, json_data):
		headers = {
			'Authorization': self.AuthToken,
			'Accept': 'application/json',
			'Content-Type': 'application/json',
		}

		#set-up our url
		feed_url = "http://" + self.MispUrl + "/feeds/add"

		async with session.post(
				feed_url,
				json=json_data,
				headers=headers
		) as response:

			if response.status != 200:
				data = await response.text()
				L.error("Failed to add Feed {} from {}\n{}".format(response.status, url, data))

			return await response.json()

	async def enable_feeds(self, feed_id, json_data):
		headers = {
			'Authorization': self.AuthToken,
			'Accept': 'application/json',
			'Content-Type': 'application/json',
		}

		feed_url = "http://" + self.MispUrl + "/feeds/enable/" + feed_id
		async with session.post(
				feed_url,
				json=json_data,
				headers=headers
		) as response:

			if response.status != 200:
				data = await response.text()
				L.error("Failed to enable Feed {} from {}\n{}".format(response.status, url, data))

			return await response.json()
