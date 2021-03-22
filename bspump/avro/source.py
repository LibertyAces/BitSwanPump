import fastavro
from ..file.fileabcsource import FileABCSource


class AvroSource(FileABCSource):

	ConfigDefaults = {
		'path': './*.avro',
		'post': 'noop',  # one of 'delete', 'noop' and 'move'
	}

	# TODO: Use the schema

	async def read(self, filename, f):
		while True:
			avro_reader = fastavro.reader(f)
			for record in avro_reader:
				await self.process(record, {
					"filename": filename
				})
