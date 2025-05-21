import csv
import io
import os

from .abcsource import HTTPABCClientSource


class HTTPClientSource(HTTPABCClientSource):

	async def read(self, response):
		response = await response.read()
		await self.process(response)


class HTTPClientTextSource(HTTPABCClientSource):

	ConfigDefaults = {
		'encoding': '',
	}

	def __init__(self, app, pipeline, id=None, config=None, headers={}):
		super().__init__(app, pipeline, id=id, config=config, headers={})

		self.encoding = self.Config['encoding']
		if self.encoding == '':
			self.encoding = None

	async def read(self, response):
		response = await response.text(encoding=self.encoding)
		await self.process(response)


class HTTPClientLineSource(HTTPClientTextSource):


	async def read(self, response):
		response = await response.text(encoding=self.encoding)

		for line in response.split('\n'):
			await self.process(line.rstrip())


class HTTPClientCSVSource(HTTPClientTextSource):

	ConfigDefaults = {
		'encoding': '',
		'mode': 'r',
		'newline': '',  # Required by CSV parser
		'dialect': 'excel',
		'delimiter': ',',
		'doublequote': True,
		'escapechar': "\\",  # Python >3.11 does not allow empty value
		'lineterminator': os.linesep,
		'quotechar': '"',
		'quoting': csv.QUOTE_MINIMAL,
		'skipinitialspace': False,
		'strict': False,
	}


	def __init__(self, app, pipeline, id=None, config=None, headers={}):
		super().__init__(app, pipeline, id=id, config=config, headers={})
		self.Dialect = csv.get_dialect(self.Config['dialect'])


	def reader(self, f):
		"""
		Description:

		**Parameters**

		f :

		:returns: ??

		|

		"""
		kwargs = {}

		v = self.Config.get('delimiter')
		if v is not None:
			kwargs['delimiter'] = v

		v = self.Config.get('doublequote')
		if v is not None:
			kwargs['doublequote'] = v

		v = self.Config.get('escapechar')
		if v is not None:
			kwargs['escapechar'] = v

		v = self.Config.get('lineterminator')
		if v is not None:
			kwargs['lineterminator'] = v

		v = self.Config.get('quotechar')
		if v is not None:
			kwargs['quotechar'] = v

		v = self.Config.get('quoting')
		if v is not None:
			kwargs['quoting'] = v

		v = self.Config.get('skipinitialspace')
		if v is not None:
			kwargs['skipinitialspace'] = v

		v = self.Config.get('strict')
		if v is not None:
			kwargs['strict'] = v

		return csv.DictReader(
			f,
			dialect=self.Dialect,
			**kwargs
		)


	async def read(self, response):
		response = await response.text(encoding=self.encoding)
		response_io = io.StringIO(response)  # Convert string to file-like object

		for line in self.reader(response_io):
			await self.process(line)
