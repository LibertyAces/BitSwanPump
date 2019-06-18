from bspump import Processor
import collections
import mongoquery


class LatchProcessor(Processor):
	"""
		Latch accumulates events in the queue of maximum specified size - `queue_max_size`

		If `queue_max_size` is 0 then queue is not limited

		If accumulated events exceeds `queue_max_size` then first event is dropped.

		The queue can be filled based on the query (empty by default). The query is mongo-like,
		see the rules in `ContentFilter`. If inclusive is True (default), matched with the query event is 
		added to the queue, otherwise skipped.

		The query may be injected with an API call to allow to control events in the queue.
		 
	"""

	ConfigDefaults = {
		'queue_max_size': 50,  # 0 means unlimited size
	}

	def __init__(self, app, pipeline, id=None, config=None):
		super().__init__(app, pipeline, query={}, inclusive=True, id=id, config=config)
		self.Inclusive = inclusive
		max_size = int(self.Config.get('queue_max_size'))
		if max_size == 0:
			self.Queue = collections.deque()
		else:
			self.Queue = collections.deque(maxlen=max_size)

		# Check if the query is correctly implemented		
		try:
			self.Query = mongoquery.Query(query)
			self.Query.match({})
		except mongoquery.QueryError:
			L.warn("Incorrect query")
			raise
		

	def process(self, context, event):
		if self.Query.match(event) == self.Inclusive:
			self.Queue.append(event)
		return event


