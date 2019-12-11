import logging
import os
import json
from asab.timer import Timer
import pyarrow as pa
import pyarrow.parquet as pq
import pandas as pd
from bspump.abc.sink import Sink

#

L = logging.getLogger(__file__)

#


class ParquetSink(Sink):
	"""
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
		'rollover_mechanism': 'rows',  # or time
		'rows_per_file': 10000,
		'writing_period': '1d',  # only used if rollover_mechanism == 'time', valid units are s, m, h, d, w
		'file_name_template': './sink{index}.parquet',
	}

	def __init__(self, app, pipeline, id=None, config=None):
		super().__init__(app, pipeline, id=id, config=config)
		app.PubSub.subscribe("Application.tick/10!", self.on_tick)

		metrics_service = app.get_service('asab.MetricsService')
		self.Counter = metrics_service.create_counter(
			"counter", tags={},
			init_values={'parquet.error': 0})
		self.Gauge = metrics_service.create_gauge(
			"gauge", tags={},
			init_values={'parquet.missing_attributes': 0, 'parquet.new_attributes': 0})

		self.Frames = []
		self.ChunkSize = self.Config['rows_in_chunk']
		self.Index = 0
		self.RolloverMechanism = self.Config['rollover_mechanism']
		self.FileNameTemplate = self.Config['file_name_template']

		self.MissingSet = set()
		self.NewSet = set()

		self.SchemaFile = self.Config.get('schema_file')
		if self.SchemaFile is not None:
			self.SchemaDefined = True
		else:
			self.SchemaDefined = False

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

		elif self.RolloverMechanism == 'time':
			writing_period = self.Config['writing_period']

			seconds_per_unit = {"s": 1, "m": 60, "h": 3600, "d": 86400, "w": 604800}

			def convert_to_seconds(s):
				return int(s[:-1]) * seconds_per_unit[s[-1]]

			writing_period = convert_to_seconds(writing_period)

			self._writing_timer = Timer(app, self.rotate_async, autorestart=True)
			self._writing_timer.start(writing_period)

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
								float, int, list, decimal, date, time, bytearray or array. Not {}'.format(col['type']))

					return False

			return True

		else:
			L.warning('No SchemaFile specified')
			return False

	def apply_schema(self, event):

		data = {}

		for attr_name, attr_descr in self.Schema.items():
			value = event.pop(attr_name, None)

			if value is None:
				data[attr_name] = None
				self.MissingSet.add(attr_name)

			else:
				value_type = attr_descr['type']
				try:
					if value_type == 'string' and type(value) is not str:
						data[attr_name] = str(value)
						continue

					if value_type == 'int' and type(value) is not int:
						data[attr_name] = int(float(value))
						continue

					if value_type == 'float' and type(value) is not float:
						data[attr_name] = float(value)
						continue

					if value_type == 'bool' and type(value) is not bool:
						if type(value) is str and value.lower() == 'false':
							data[attr_name] = False
							continue
						else:
							data[attr_name] = bool(value)
							continue

				except ValueError:
					self.Counter.add('parquet.error', 1)
					pass

				data[attr_name] = value

		new_attrs_count = len(event)
		if new_attrs_count > 0:
			self.NewSet = self.NewSet.union([k for k in event])

		df = pd.DataFrame([data])
		return df

	def build_filename(self, postfix=''):
		return self.FileNameTemplate.format(
			index=('{:04d}'.format(self.Index)) if self.Index is not None else ''
		) + postfix

	def on_tick(self, event_name):
		self.Gauge.set('parquet.new_attributes', len(self.NewSet))
		self.Gauge.set('parquet.missing_attributes', len(self.MissingSet))
		self.flush()

	def process(self, context, event):

		if self.SchemaDefined:
			df = self.apply_schema(event)
		else:
			df = pd.DataFrame([event])
		self.Frames.append(df)

		if self.RolloverMechanism == 'rows' and (len(self.Frames) >= self.ChunkSize):

			self.Chunks = self.Chunks + 1
			if self.Chunks >= self.ChunksPerFile:
				self.rotate()

			self.flush()

	def flush(self):
		if len(self.Frames) != 0:
			table = pa.Table.from_pandas(pd.concat(self.Frames))
			if self._pq_writer is None:
				self._pq_writer = pq.ParquetWriter(self.build_filename('-open'), table.schema)
			try:
				self._pq_writer.write_table(table=table)
			except Exception as e:
				L.warning(e)
			self.Frames = []

	async def rotate_async(self):
		self.rotate()

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
			self.Chunks = 0

		self.Index = self.Index + 1
