from bspump import Processor
import collections
import mongoquery


class LatchProcessor(Processor):
	"""
		Latch accumulates events in the Latch of maximum specified size - `latch_max_size`

		If `latch_max_size` is 0 then latch is not limited

		If accumulated events exceeds `latch_max_size` then first event is dropped.

		The latch can be filled based on the query (empty by default). The query is mongo-like,
		see the rules in `ContentFilter`. If the query is True (default), then all events are added to the latch.
		If it is False, all events will be skipped. Dictionary-like query is executed as filter.

		The query can be injected with an API call to allow to control events in the latch.

	"""

	ConfigDefaults = {
		'latch_max_size': 50,  # 0 means unlimited size
	}

	def __init__(self, app, pipeline, id=None, config=None):
		super().__init__(app, pipeline, query=True, id=id, config=config)
		self.Inclusive = inclusive
		max_size = int(self.Config.get('latch_max_size'))
		if max_size == 0:
			self.Latch = collections.deque()
		else:
			self.Latch = collections.deque(maxlen=max_size)

		# Check if the query is correctly implemented
		if (query == True) or (query == False):
			self.Query = query
		else:
			try:
				self.Query = mongoquery.Query(query)
				self.Query.match({})
			except mongoquery.QueryError:
				L.warn("Incorrect query")
				raise
		

	def process(self, context, event):
		if self.Query == True:
			self.Latch.append(event)
		
		elif self.Query == False:
			return event
		
		elif self.Query.match(event) == self.Inclusive:
			self.Latch.append(event)
		return event


