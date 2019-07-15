from unittest.mock import patch, call

import bspump.file
import bspump.unittest


class CustomFileBlockSink(bspump.file.FileBlockSink):

	ConfigDefaults = {
		"path": "/path/doesn't/exists.csv"
	}


class TestFileBlockSink(bspump.unittest.ProcessorTestCase):
	@patch("bspump.file.fileblocksink.os.open")
	def test_file_block_sink(self, mocked_os_open):
		mocked_os_open.return_value = 3  # File descriptor
		events = [
			(None, b'deadc0de'),
		]

		self.set_up_processor(CustomFileBlockSink)
		with patch("bspump.file.fileblocksink.os.fdopen") as mock_file:
			output = self.execute(
				events
			)
			self.assertIn(
				call().__enter__().write(b'deadc0de'),
				mock_file.mock_calls
			)
			self.assertEqual(mock_file.call_args, call(3, "wb"))
			self.assertEqual(output, [])
