import collections
import logging

import mongoquery

from .analyzer import Analyzer

###

L = logging.getLogger(__name__)


###

class LatchAnalyzer(Analyzer):
	"""
		The `LatchAnalyzer` accumulates events in the `Latch` variable.
		The `Latch` is a queue of maximum size specified in configuration - `latch_max_size`

		If `latch_max_size` is 0 then `Latch` is not limited

		If accumulated events exceeds `latch_max_size` then first event is dropped.

		`Latch` can be filled based on the `query` variable (True by default).
		The query may be:
		1. `True`, then all events will be added to `Latch`.
		2. `False`, all events will be skipped.
		3. Dictionary, following the mongo-like query syntaxis (see the rules in `ContentFilter`).
		In this case only events matched with this query will be added to the `Latch`.

		The query can be injected with an API call to allow to control events in the latch.

	"""

	ConfigDefaults = {
		'latch_max_size': 50,  # 0 means unlimited size
	}

	def __init__(self, app, pipeline, query=True, analyze_on_clock=False, inclusive=False, id=None, config=None):
		super().__init__(app, pipeline, analyze_on_clock=analyze_on_clock, id=id, config=config)
		max_size = int(self.Config.get('latch_max_size'))
		if max_size == 0:
			self.Latch = collections.deque()
		else:
			self.Latch = collections.deque(maxlen=max_size)

		# Check if the query is correctly implemented
		if isinstance(query, bool):
			self.Query = query
		else:
			try:
				self.Query = mongoquery.Query(query)
				self.Query.match({})
			except mongoquery.QueryError:
				L.warning("Incorrect query")
				raise

		self.Inclusive = inclusive


	def process(self, context, event):
		if self.Query is True:
			self.Latch.append(event)

		elif self.Query is False:
			return event

		elif self.Query.match(event) != self.Inclusive:
			self.Latch.append(event)
		return event
