from unittest.mock import patch, call

import bspump.file
import bspump.unittest


class CustomFileCSVSink(bspump.file.FileCSVSink):

	ConfigDefaults = {
		"path": "/path/doesn't/exists.csv"
	}


class TestFileCSVSink(bspump.unittest.ProcessorTestCase):
	def test_file_csv_sink(self):
		events = [
			(None, {"key": "value"}),
		]

		self.set_up_processor(CustomFileCSVSink)
		with patch("bspump.file.filecsvsink.open") as mock_file:
			output = self.execute(
				events
			)
			self.assertIn(
				call().write('key\n'),
				mock_file.mock_calls
			)
			self.assertIn(
				call().write('value\n'),
				mock_file.mock_calls
			)
			self.assertEqual(mock_file.call_args, call("/path/doesn't/exists.csv", "w", newline=""))
			self.assertEqual(output, [])
