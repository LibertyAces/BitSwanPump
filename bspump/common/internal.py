from ..abcproc import Source


class InternalSource(Source):


	ConfigDefaults = {
	}


	def __init__(self, app, pipeline, id=None, config=None):
		super().__init__(app, pipeline, id=id, config=config)


	async def start(self):
		pass
