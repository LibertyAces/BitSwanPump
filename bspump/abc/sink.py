from .processor import ProcessorBase

class Sink(ProcessorBase):
	
	@classmethod
	def construct(cls, app, pipeline, definition:dict):
		newid = definition.get('id')
		config = definition.get('config')
		return cls(app, pipeline, newid, config)
