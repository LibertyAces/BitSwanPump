import fastavro
from ..avro import loader
from ..file.fileabcsource import FileABCSource
import logging



###

L = logging.getLogger(__name__)

###


class AvroSource(FileABCSource):

	ConfigDefaults = {
		'path': './*.avro',
		'post': 'noop',  # one of 'delete', 'noop' and 'move'
		'schema_file': '',
	}

	def __init__(self, app, pipeline, id=None, config=None):
		super().__init__(app, pipeline, id=id, config=config)
		self.Schema = loader.load_avro_schema(self.Config)
	async def read(self, filename, f):
		while True:

			if self.Schema is None:
				L.warning("Schema file is not provided.")
			else:
				L.warning("Schema file is used.")

			avro_reader = fastavro.reader(f,self.Schema)
			for record in avro_reader:
				await self.process(record, {
					"filename": filename
				})
