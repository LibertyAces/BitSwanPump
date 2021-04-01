import fastavro
from ..avro import loader
from ..file.fileabcsource import FileABCSource


class AvroSource(FileABCSource):

	ConfigDefaults = {
		'path': './*.avro',
		'post': 'noop',  # one of 'delete', 'noop' and 'move'
	}

	def __init__(self, app, pipeline, id=None, config=None):
		super().__init__(app, pipeline, id=id, config=config)
		self.Schema = loader.load_avro_schema(self.Config)


	async def read(self, filename, f):
		while True:
			avro_reader = fastavro.reader(f,self.Schema)
			for record in avro_reader:
				await self.process(record, {
					"filename": filename
				})
