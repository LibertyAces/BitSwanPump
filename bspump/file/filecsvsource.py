import csv
import logging
import os

from .fileabcsource import FileABCSource


L = logging.getLogger(__file__)


class FileCSVSource(FileABCSource):


	ConfigDefaults = {
		'mode': 'r',
		'newline': '',  # Required by CSV parser
		'dialect': 'excel',
		'delimiter': ',',
		'doublequote': True,
		'escapechar': "",
		'lineterminator': os.linesep,
		'quotechar': '"',
		'quoting': csv.QUOTE_MINIMAL,
		'skipinitialspace': False,
		'strict': False,
	}


	def __init__(self, app, pipeline, fieldnames=None, id=None, config=None):
		super().__init__(app, pipeline, id=id, config=config)

		self.Dialect = csv.get_dialect(self.Config['dialect'])
		self.FieldNames = fieldnames


	def reader(self, f):
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
			fieldnames=self.FieldNames,
			**kwargs
		)


	async def read(self, filename, f):

		for line in self.reader(f):
			await self.process(line, {
				"filename": filename
			})

			await self.simulate_event()
