from ..abc.processor import Processor
import asab
import mongoquery

###

L = logging.getLogger(__name__)

###

class ContentFilter(Processor):
	'''
	This is processor implenting a simple attribute filter.
	If 'inclusive' is False, all fields from event matching with lookup will be deleted, 
	otherwise all fields not from lookup will be deleted from event. 
	'''

	def __init__(self, app, pipeline, query=None, id=None, config=None):
		super().__init__(app, pipeline, id=id, config=config)
		if query is None:
			query = {}
		
		try:
			self.Query = mongoquery.Query(query)
			self.Query.match({})
		except mongoquery.QueryError:
			L.warn("Incorrect query")
			raise


	def predicate(self, event):
		return True


	def do_on_hit(self, event):
		return event


	def do_on_miss(self, event):
		return event


	def execute_query(self, event):
		matched = self.Query.match(event)
		if matched:
			new_event = self.do_on_hit(event)
		else:
			new_event = self.do_on_miss(event)

		return new_event

	
	def process(self, context, event):
		if not self.predicate(event):
			return event
		
		return self.execute_query(event)
