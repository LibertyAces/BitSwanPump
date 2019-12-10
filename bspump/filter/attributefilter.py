import logging

from ..abc.processor import Processor

###

L = logging.getLogger(__name__)

###


class AttributeFilter(Processor):
	'''
	This is processor implenting a simple attribute filter.
	If 'inclusive' is False, all fields from event matching with lookup will be deleted,
	otherwise all fields not from lookup will be deleted from event.
	'''

	def __init__(self, app, pipeline, lookup=None, inclusive=False, id=None, config=None):
		super().__init__(app, pipeline, id=id, config=config)
		self.Inclusive = inclusive

		# Lookups discovery
		if lookup is not None:
			svc = app.get_service("bspump.PumpService")
			self.Lookup = svc.locate_lookup(lookup)
		else:
			self.Lookup = None


	def predicate(self, event):
		return True


	def get_fields(self, event):
		return set()


	def filter_fields(self, event):
		fields = self.get_fields(event)
		for event_key in list(event):
			if (event_key in fields) != self.Inclusive:
				event.pop(event_key)
		return event


	def process(self, context, event):
		if not self.predicate(event):
			return event

		return self.filter_fields(event)
