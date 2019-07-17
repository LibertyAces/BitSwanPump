from unittest import mock
from unittest.mock import patch, mock_open

import bspump.avro
import bspump.unittest


class CustomAvroSink(bspump.avro.AvroSink):
	ConfigDefaults = {
		"schema_file": "/file/doesn't/exist.avro"
	}


class TestAvroSink(bspump.unittest.ProcessorTestCase):
	@patch("bspump.avro.sink.os.rename")
	@patch("bspump.avro.sink.writer")
	@patch("bspump.avro.sink.open")
	def test_avro_sink(self, mock_file, mock_writer, mock_rename):
		event = {"name": "John Wick", "favorite_number":  666, "favorite_color": None}
		events = [
			(None, event),
		]

		read_schema = """{
			"namespace": "example.avro",
			"type": "record",
			"name": "User",
			"fields": [
				{"name": "name", "type": "string"},
				{"name": "favorite_number",  "type": ["int", "null"]},
				{"name": "favorite_color", "type": ["string", "null"]}
			]
		}"""

		parsed_schema = {
			'type': 'record',
			'name': 'example.avro.User',
			'fields': [
				{'name': 'name', 'type': 'string'},
				{'name': 'favorite_number', 'type': ['int', 'null']},
				{'name': 'favorite_color', 'type': ['string', 'null']}
			], '__fastavro_parsed': True}

		mock_file.side_effect = (
			mock_open(read_data=read_schema).return_value,
			mock_open(read_data=None).return_value
		)

		self.set_up_processor(CustomAvroSink)

		output = self.execute(
			events
		)

		self.assertEqual(
			[event for context, event in output],
			[]
		)

		mock_writer.assert_called_once_with(mock.ANY, parsed_schema, [event])

		self.Pipeline.Processor.rotate()

		mock_rename.assert_called_once_with('./sink.avro-open', './sink.avro')

