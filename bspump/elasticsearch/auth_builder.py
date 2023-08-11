import aiohttp
import logging
import ssl

import asab


L = logging.getLogger(__name__)


class AuthBuilder:
	

	def __init__(self, username, password, api_key, cafile):
		self.username = username
		self.password = password
		self.api_key = api_key
		self.cafile = cafile


	def build_headers(self):

	# Check configurations
		if self.username != '' and self.api_key != '':
			raise ValueError("Both username and API key can't be specified. Please choose one option.")

		# Build headers
		if self.username != '':
			self._auth = aiohttp.BasicAuth(self.username, self.password)
			L.log(asab.LOG_NOTICE, 'Building basic authorization with username/password')
			self.Headers = {
				'Content-Type': 'application/json',
			}
		elif self.api_key != '':
			self._auth = None
			self.Headers = {
				'Content-Type': 'application/json',
				"Authorization": 'ApiKey {}'.format(self.api_key)
			}
			L.log(asab.LOG_NOTICE, 'Building headers with api_key')
		else:
			self._auth = None
			self.Headers = None

		return self.Headers, self._auth


	def build_ssl_context(self):

		if self.cafile != '':
			self.SSLContext = ssl.create_default_context(cafile=self.cafile)
		else:
			L.log(asab.LOG_NOTICE, 'SSL certificate path is not specified')
			return None
		
		return self.SSLContext


	def apply_ssl_context(self, url):
		if url.startswith('https://'):
			ssl_context = self.SSLContext
		else:
			ssl_context = None

		return ssl_context