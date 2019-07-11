import tableausdk
import datetime
import logging
import os.path
from ..abc.sink import Sink

#

L = logging.getLogger(__file__)

#

class FileTableauSink(Sink):

	ConfigDefaults = {
		'path': '',
		'table_name': 'Table',
	}

	def __init__(self, app, pipeline, id=None, config=None):
		super().__init__(app, pipeline, id=id, config=config)
		self.DataExtract = None
		self.DataSchema = None
		self.Table = None
		self.ColumnMapping = {}


	def get_file_name(self, context, event):
		'''
			Override this method to gain control over output file name.
		'''
		return self.Config['path']

	
	def set_data_schema(self, data_names, data_types):
		self.ColumnMapping = {}
		for i, name in enumerate(data_names):
			self.ColumnMapping[key] = i
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
					L.warn("Wrong type {} detected".format(field_type))
	

	def set_row(self, context, event):
		row = tableausdk.Extract.Row(self.DataSchema)
		for key in event.keys():
			field_value = event[key]['value']
			field_type = event[key]['type']
			if field_value is None:
				row.setNull(self.ColumnMapping[field_type])
			elif field_type == 'boolean':
				row.setBoolean(self.ColumnMapping[field_type], field_value)
			elif field_type == 'charstring':
				row.setCharString(self.ColumnMapping[field_type], field_value)
			elif field_type == 'date':
				# field_value must be timestamp
				t_t = datetime.datetime.fromtimestamp(t).timetuple()
				row.setDate(self.ColumnMapping[field_type], t_t[0], t_t[1], t_t[2])
			elif field_type == 'datetime':
				# field_value must be timestamp
				t_t = datetime.datetime.fromtimestamp(t).timetuple()
				frac = (field_value - int(field_value)) / 10 #	The fraction of a second as one tenth of a millisecond (1/10000)
				row.setDateTime(self.ColumnMapping[field_type], t_t[0], t_t[1], t_t[2], t_t[3], t_t[4], t_t[5], frac)
			elif field_type == 'double':
				row.setDouble(self.ColumnMapping[field_type], field_value)
			elif field_type == 'duration':
				# must be in seconds
				frac = (field_value - int(field_value)) / 10
				field_value = int(field_value)
				days = int(field_value / (24 * 60 * 60))
				hours = days * 24
				minutes = hours * 60
				seconds = minutes * 60
				row.setDuration(self.ColumnMapping[field_type], days, hours, minutes, seconds, frac)
			elif field_type == 'integer':
				row.setInteger(self.ColumnMapping[field_type], field_value)
			elif field_type == 'spatial':
				row.setSpatial(self.ColumnMapping[field_type], field_value)
			elif field_type == 'unicodestring':
				row.setString(self.ColumnMapping[field_type], field_value)
			else:
				L.warn("Wrong type in event {} detected".format(field_type))

		self.Table.insert(row)


	def process(self, context, event):
		if self.DataExtract is None:
			if not os.path.isfile(self.get_file_name()):
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