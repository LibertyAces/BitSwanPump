from .processor import ProcessorBase


class Sink(ProcessorBase):
	"""
	Sink object serves as a final event destination within the pipeline given.
	Subsequently, the event is dispatched/written into the system by the BSPump.
	"""
	pass
