from fastavro import writer, parse_schema
from fastavro.validation import validate_many
import json
import logging
import os
from bspump.abc.sink import Sink

L = logging.getLogger(__name__)


class AvroSink(Sink):

	"""
	Apache Avro™ is a data serialization system.

	Avro relies on schemas defined with JSON.
	Schemas are composed of primitive types null, boolean, int, long, float, double, bytes,
	and string and complex types (record, enum, array, map, union, and fixed).
	You can learn more about Avro from their documentation - https://avro.apache.org/docs/current/

	Avro schema example:
		{
			"namespace": "example.avro",
			"type": "record",
			"name": "User",
			"fields": [
				{"name": "name", "type": "string"},
				{"name": "favorite_number",  "type": ["int", "null"]},
				{"name": "favorite_color", "type": ["string", "null"]}
			]
		}

	File Types:
	.avro - Avro Serialized Data
	.avsc - Avro Schema

	"""
	ConfigDefaults = {
		'file_name_template': './sink{index}.avro',
		'events_per_file': 1000,
		'events_per_chunk': 100,
		'rollover_mechanism': 'none'  # or chunks
	}

	def __init__(self, app, pipeline, id=None, config=None):
		super().__init__(app, pipeline, id=id, config=config)

		self.SchemaFile = self.Config.get('schema_file')
		if self.SchemaFile is None:
			L.error('schema is not defined')
			raise FileNotFoundError

		if self.SchemaFile is not None:
			schema = json.load(open(self.SchemaFile, 'r'))
			self.Schema = parse_schema(schema)
			'''with open(self.SchemaFile) as json_data:
				schema = json.loads(json_data.read())
				self.Schema = parse_schema(schema)'''

		self.RolloverMechanism = self.Config.get('rollover_mechanism')
		self.FileNameTemplate = self.Config['file_name_template']
		self.Events = []  # list of events
		self.EventsPerFile = self.Config['events_per_file']
		self.ChunkSize = self.Config['events_per_chunk']
		self._filemode = 'wb'

		if self.RolloverMechanism == 'chunks':

			if self.EventsPerFile % self.ChunkSize != 0:
				self.ChunksPerFile = int(round(self.EventsPerFile / self.ChunkSize))
				L.warning('events_per_file % events_per_chunk needs to be zero. events_per_file was rounded')
			elif self.EventsPerFile < self.ChunkSize:
				self.ChunksPerFile = 1
				L.warning('events_per_file needs to be equal or greater than events_per_chunk, events_per_file changed to events_per_chunk value')
			elif self.EventsPerFile >= self.ChunkSize:
				self.ChunksPerFile = int(self.EventsPerFile / self.ChunkSize)
			else:
				L.warning('invalid events_per_file - {} or events_per_chunk - {} '.format(self.EventsPerFile, self.ChunkSize))
				self.ChunksPerFile = 1

			self.Chunks = 0
			self.Index = 0
		else:
			if self.RolloverMechanism != 'none':
				L.warning('Unknown rollover mechanism {} - defaulting to none'.format(
					self.RolloverMechanism, self.ConfigDefaults['rollover_mechanism']))

			self.RolloverMechanism = 'none'
			self.Index = None
			self.Chunks = None

	def build_filename(self, postfix=''):
		return self.FileNameTemplate.format(
			index=('{:04d}'.format(self.Index)) if self.Index is not None else ''
		) + postfix

	def flush(self):
		if len(self.Events) != 0:
			if self.SchemaFile is not None:
				try:
					is_valid = validate_many(self.Events, self.Schema)
					if is_valid is True:
						with open(self.build_filename('-open'), self._filemode) as out:
							writer(out, self.Schema, self.Events)
						if self._filemode == 'wb':
							self._filemode = 'a+b'
				except Exception as e:
					L.error(e)

			self.Events = []

	def process(self, context, event):
		self.Events.append(event)

		if self.RolloverMechanism == 'chunks':
			if len(self.Events) >= self.EventsPerFile:
				self.Chunks = self.Chunks + 1
				if self.Chunks >= self.ChunksPerFile:
					self.rotate()
		self.flush()

	def rotate(self, new_filename=None):
		'''
			Call this to close the currently open file.
		'''

		self.flush()

		current_fname = self.build_filename('-open')
		os.rename(current_fname, current_fname[:-5])

		if self.RolloverMechanism == 'chunks':
			self.Index = self.Index + 1
		self._filemode = 'wb'
