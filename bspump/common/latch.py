from bspump import Processor
import collections
import mongoquery


class LatchProcessor(Processor):
	"""
		Latch accumulates events in the queue of maximum specified size - `queue_max_size`

		If `queue_max_size` is 0 then queue is not limited

		If accumulated events exceeds `queue_max_size` then first event is dropped
	"""

	ConfigDefaults = {
		'queue_max_size': 50,  # 0 means unlimited size
	}

	def __init__(self, app, pipeline, id=None, config=None):
		super().__init__(app, pipeline, query={}, id=id, config=config)
		max_size = int(self.Config.get('queue_max_size'))
		if max_size == 0:
			self._Queue = collections.deque()
		else:
			self._Queue = collections.deque(maxlen=max_size)

		# Check if the query is correctly implemented
		
		try:
			self.Query = mongoquery.Query(query)
			self.Query.match({})
		except mongoquery.QueryError:
			L.warn("Incorrect query")
			raise
		

	def process(self, context, event):
		if self.Query.match(event):
			self._Queue.append(event)
		return event


	def list_queue(self, query=None):
		if query is not None:
			try:
				self.Query = mongoquery.Query(query)
				self.Query.match({})
			except mongoquery.QueryError:
				L.warn("Incorrect query")
				raise
		return list(self._Queue)

