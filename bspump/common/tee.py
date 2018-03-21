import copy
from ..abcproc import Processor
from .internal import InternalSource


class TeeProcessor(Processor):


	ConfigDefaults = {
	}


	def __init__(self, app, pipeline, target, id=None, config=None):
		super().__init__(app, pipeline, id=id, config=config)

		self.Source = None

		self._target = target
		self._svc = app.get_service("bspump.PumpService")


	def start(self):
		if self.Source is None:
			target = self._svc.Pipelines.get(self._target)
			#TODO: Handle None

			for source in target.Sources:
				if not isinstance(source, InternalSource): continue
				self.Source = source
				break

			#TODO: Handle self.Source is None


	def process(self, event):
		event_copy = copy.deepcopy(event)
		self.Source.put_nowait(event_copy)
		return event
