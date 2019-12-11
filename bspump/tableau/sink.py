import tableausdk
import tableausdk.Extract
import tableausdk.Types
import tableausdk.Exceptions
import asab
import datetime
import logging
import os.path
from ..abc.sink import Sink


L = logging.getLogger(__file__)


class FileTableauSink(Sink):

	ConfigDefaults = {
		'path': '',
		'rotate_period': 1,
		'table_name': 'Extract',
	}

	def __init__(self, app, pipeline, id=None, config=None):
		super().__init__(app, pipeline, id=id, config=config)
		self.DataExtract = None
		self.DataSchema = None
		self.Table = None
		self.ColumnMapping = {}
		self.RotatePeriod = int(self.Config['rotate_period'])
		self.Timer = asab.Timer(app, self.on_clock_tick, autorestart=True)
		self.Timer.start(self.RotatePeriod)


	async def on_clock_tick(self):
		self.rotate()


	def get_file_name(self, context, event):
		'''
			Override this method to gain control over output file name.
		'''
		return self.Config['path']


	def set_data_schema(self, data_names, data_types):
		self.ColumnMapping = {}
		for i, name in enumerate(data_names):
			self.ColumnMapping[name] = i
			field_type = data_types[i]
			if field_type == 'boolean':
				self.DataSchema.addColumn(name, tableausdk.Types.Type.BOOLEAN)
			elif field_type == 'charstring':
				self.DataSchema.addColumn(name, tableausdk.Types.Type.CHAR_STRING)
			elif field_type == 'date':
				self.DataSchema.addColumn(name, tableausdk.Types.Type.DATE)
			elif field_type == 'datetime':
				self.DataSchema.addColumn(name, tableausdk.Types.Type.DATETIME)
			elif field_type == 'double':
				self.DataSchema.addColumn(name, tableausdk.Types.Type.DOUBLE)
			elif field_type == 'duration':
				self.DataSchema.addColumn(name, tableausdk.Types.Type.DURATION)
			elif field_type == 'integer':
				self.DataSchema.addColumn(name, tableausdk.Types.Type.INTEGER)
			elif field_type == 'spatial':
				self.DataSchema.addColumn(name, tableausdk.Types.Type.SPATIAL)
			elif field_type == 'unicodestring':
				self.DataSchema.addColumn(name, tableausdk.Types.Type.UNICODE_STRING)
			else:
				L.warning("Wrong type {} detected".format(field_type))


	def set_row(self, context, event):
		row = tableausdk.Extract.Row(self.DataSchema)
		for key in event.keys():
			field_value = event[key]['value']
			field_type = event[key]['type']
			if field_value is None:
				row.setNull(self.ColumnMapping[key])
			elif field_type == 'boolean':
				row.setBoolean(self.ColumnMapping[key], field_value)
			elif field_type == 'charstring':
				row.setCharString(self.ColumnMapping[key], field_value)
			elif field_type == 'date':
				# field_value must be timestamp
				t_t = datetime.datetime.fromtimestamp(field_value).timetuple()
				row.setDate(self.ColumnMapping[key], t_t[0], t_t[1], t_t[2])
			elif field_type == 'datetime':
				# field_value must be timestamp
				t_t = datetime.datetime.fromtimestamp(event[key]['value']).timetuple()
				frac = int((field_value - int(field_value)) * 10000)  # The fraction of a second as one tenth of a millisecond (1/10000)
				row.setDateTime(self.ColumnMapping[key], t_t[0], t_t[1], t_t[2], t_t[3], t_t[4], t_t[5], frac)
			elif field_type == 'double':
				row.setDouble(self.ColumnMapping[key], field_value)
			elif field_type == 'duration':
				# must be in seconds
				frac = (field_value - int(field_value)) / 10
				field_value = int(field_value)
				days = int(field_value / (24 * 60 * 60))
				hours = days * 24
				minutes = hours * 60
				seconds = minutes * 60
				row.setDuration(self.ColumnMapping[key], days, hours, minutes, seconds, frac)
			elif field_type == 'integer':
				row.setInteger(self.ColumnMapping[key], field_value)
			elif field_type == 'spatial':
				row.setSpatial(self.ColumnMapping[key], field_value)
			elif field_type == 'unicodestring':
				row.setString(self.ColumnMapping[key], field_value)
			else:
				L.warning("Wrong type in event {} detected".format(field_type))

		self.Table.insert(row)


	def process(self, context, event):
		if self.DataExtract is None:
			if not os.path.isfile(self.get_file_name(context, event)):
				# create table
				self.DataExtract = tableausdk.Extract.Extract(self.get_file_name(context, event))
				self.DataSchema = tableausdk.Extract.TableDefinition()
				data_types = [event[key]['type'] for key in event.keys()]
				self.set_data_schema(event.keys(), data_types)
				self.Table = self.DataExtract.addTable(self.Config['table_name'], self.DataSchema)
			else:
				# get data_extract from table
				self.DataExtract = tableausdk.Extract.Extract(self.get_file_name(context, event))
				self.Table = self.DataExtract.openTable(self.Config['table_name'])
				self.DataSchema = self.Table.getTableDefinition()
				column_count = self.DataSchema.getColumnCount()
				self.ColumnMapping = {}
				for i in range(0, column_count):
					self.ColumnMapping[self.DataSchema.getColumnName(i)] = i

		self.set_row(context, event)


	def rotate(self):
		'''
			Call this to close the currently open file.
		'''
		if self.DataExtract is not None:
			self.DataExtract.close()
			del self.DataExtract
			self.DataExtract = None
			self.DataSchema = None
			self.Table = None
			self.ColumnMapping = {}
