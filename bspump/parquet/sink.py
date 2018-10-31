import logging
import os
import json
import pyarrow as pa
import pyarrow.parquet as pq
import pandas as pd
from bspump.abc.sink import Sink

#

L = logging.getLogger(__file__)

#

class ParquetSink(Sink):
	""""
	schema_file is JSON which defines column names (as keys) and their types.
	These types are allowed : string, bool, float, int, list, decimal
										date, time, bytearray, array

	schema_file example:
		{
		  "name":{
			  "type": "string"
		  },
		  "age":{
			  "type": "int"
		  },
		  "salary":{
			  "type": "float"
		  }
		}

	"""

	ConfigDefaults = {
		'rows_in_chunk': 1000,
		'rollover_mechanism': 'rows',
		'rows_per_file': 10000,
		'file_name_template': './sink{index}.parquet',
	}

	def __init__(self, app, pipeline, id=None, config=None):
		super().__init__(app, pipeline, id=id, config=config)
		app.PubSub.subscribe("Application.tick/10!", self.on_tick)

		self.Frames = []
		self.ChunkSize = self.Config['rows_in_chunk']
		self.RolloverMechanism = self.Config['rollover_mechanism']
		self.FileNameTemplate = self.Config['file_name_template']

		self.SchemaFile = self.Config['schema_file']
		if self.SchemaFile is not None:
			self.SchemaDefined = True
		else:
			self.SchemaDefined = True

		self.SchemaDataTypes = ['string', 'bool', 'list', 'decimal', 'float', 'int', 'date', 'time', 'bytearray', 'array']

		if self.SchemaDefined is True:
			with open(self.SchemaFile) as json_data:
				schema = json.load(json_data)
				schema_is_valid = self.schema_validator(schema)
				print(str(schema_is_valid))
				if schema_is_valid:
					self.Schema = schema
				else:
					self.SchemaDefined = False

		if self.RolloverMechanism == 'rows':

			if self.Config['rows_per_file'] % self.ChunkSize != 0:
				self.ChunksPerFile = int(round(self.Config['rows_per_file'] / self.ChunkSize))
				L.warning('rows_per_file % rows_in_chunk needs to be zero. rows_per_file was rounded')
			elif self.Config['rows_per_file'] < self.ChunkSize:
				self.ChunksPerFile = 1
				L.warning('rows_per_file needs to be equal or greater than rows_in_chunk, rows_per_file changed to rows_in_chunk value')
			else:
				self.ChunksPerFile = int(self.Config['rows_per_file'] / self.ChunkSize)
			self.Chunks = 0
			self.Index = 0

		else:
			self.Index = None
			self.Chunks = None

		self._pq_writer = None

	def schema_validator(self, schema):

		if schema is not None:

			for col in schema.values():
				if col['type'] is None:
					L.warning('SchemaFile is not valid schema. Type not found for every column.')
					return False

				col['type'] = col['type'].lower()

				if col['type'] not in self.SchemaDataTypes:
					L.warning('SchemaFile is not valid schema. Types must be one of the following: string, bool, \
								float, int, list, decimal, date, time, bytearray or array. Not ' + col['type'])

					return False

			return True

		else:
			L.warning('No SchemaFile specified')
			return False

	def apply_schema(self, event):

		data = event
		for col, value in event.items():

			col_schema = self.Schema.get(col)
			if col_schema is None:
				L.warning(col + ' is not part of Schema File. Because of that, It is not going to be in parquet file')
				del data[col]
			else:
				if col_schema['type'] == 'string' and type(value) is not str:
					try:
						data[col] = str(value)
					except ValueError:
						del data[col]
						L.warning(col + ' cannot be converted to ' + col_schema['type']
									+ '. Because of that, It is not going to be in parquet file')
						pass
				if col_schema['type'] == 'int' and type(value) is not int:
					try:
						data[col] = int(float(value))
					except ValueError:
						del data[col]
						L.warning(col + ' cannot be converted to ' + col_schema['type']
									+ '. Because of that, It is not going to be in parquet file')
						pass
				if col_schema['type'] == 'float' and type(value) is not float:
					try:
						data[col] = float(value)
					except ValueError:
						del data[col]
						L.warning(col + ' cannot be converted to ' + col_schema['type']
									+ '. Because of that, It is not going to be in parquet file')
						pass
				if col_schema['type'] == 'bool' and type(value) is not bool:
					try:
						if type(value) is str and value.lower() == 'false':
							data[col] = False
						else:
							data[col] = bool(value)

					except ValueError:
						del data[col]
						L.warning(col + ' cannot be converted to ' + col_schema['type']
									+ '. Because of that, It is not going to be in parquet file')
						pass

		df = pd.DataFrame([data])
		return df

	def build_filename(self, postfix=''):
		return self.FileNameTemplate.format(
			index=('{:04d}'.format(self.Index)) if self.Index is not None else ''
		) + postfix

	def on_tick(self, event_name):
		self.flush()

	def process(self, context, event):

		if self.SchemaDefined:
			df = self.apply_schema(event)
		else:
			df = pd.DataFrame([event])
		self.Frames.append(df)

		if len(self.Frames) >= self.ChunkSize:

			if self.RolloverMechanism == 'rows':
				self.Chunks = self.Chunks + 1
				if self.Chunks >= self.ChunksPerFile:
					self.rotate()

			self.flush()

	def flush(self):
		if len(self.Frames) != 0:
			table = pa.Table.from_pandas(pd.concat(self.Frames))
			if self._pq_writer is None:
				self._pq_writer = pq.ParquetWriter(self.build_filename('-open'), table.schema)
			self._pq_writer.write_table(table=table)
			self.Frames = []

	def rotate(self, new_filename=None):
		'''
			Call this to close the currently open file.
		'''

		self.flush()
		del self._pq_writer
		self._pq_writer = None

		current_fname = self.build_filename('-open')
		os.rename(current_fname, current_fname[:-5])

		if self.RolloverMechanism == 'rows':
			self.Index = self.Index + 1
