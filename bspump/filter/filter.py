import abc
from ..abc.processor import Processor
import asab

###

L = logging.getLogger(__name__)

###

class Filter(Processor):
	'''
	This is processor implenting abstract filter.
	If delete_fields is True, all fields from event matching with lookup will be deleted, 
	otherwise all fields not from lookup will be deleted from event. 
	'''

	def __init__(self, app, pipeline, lookup, delete_fields=True, id=None, config=None):
		super().__init__(app, pipeline, id=id, config=config)
		self.DeleteFields = delete_fields
		
		#Lookups discovery
		svc = app.get_service("bspump.PumpService")
		self.Lookup = svc.locate_lookup(lookup)


	@abc.abstractmethod
	def predicate(self, event):
		raise NotImplemented("")

	
	@abc.abstractmethod
	def get_fields(self, event):
		# From lookup
		raise NotImplemented("")

	
	def filter_fields(self, event):
		fields = self.get_fields(event)
		for event_key in event.keys():
			if (event_key in fields) == self.DeleteFields:
				event.pop(event_key)
		return event

	
	def process(self, context, event):
		if not self.predicate(event):
			return event
		
		return self.filter_fields(event)

	