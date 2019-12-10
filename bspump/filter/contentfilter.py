import logging

import mongoquery

from ..abc.processor import Processor

###

L = logging.getLogger(__name__)

###


class ContentFilter(Processor):
	'''
		This is processor implenting a simple attribute filter.
		The query is constructed in mongodb manner.
		NB:
		Only the "/pattern/<options>" syntax is supported for $regex.
		As a consequence, $options isn’t supported.
		$text hasn’t been implemented.
		Due to the pure python nature of mongoquery, $where isn’t supported.
		The Geospatial operators $geoIntersects, $geoWithin, $nearSphere, and $near are not implemented.
		Projection operators $`, $elemMatch, $meta,
		and $slice are not implemented (only querying is implemented)
		$type is limited to recognising generic python types,
		it won’t look into recognising the format of
		the data (for instance, it doesn’t check Object ID’s format, only that they are strings).
		(from https://pypi.org/project/mongoquery/)
	'''

	def __init__(self, app, pipeline, query={}, id=None, config=None):
		super().__init__(app, pipeline, id=id, config=config)

		# Check if the query is correctly implemented
		try:
			self.Query = mongoquery.Query(query)
			self.Query.match({})
		except mongoquery.QueryError:
			L.warning("Incorrect query")
			raise


	def on_hit(self, context, event):
		'''
			This function tranforms the event, if it
			matched the query.
		'''
		return event


	def on_miss(self, context, event):
		'''
			This function tranforms the event, if it did not
			matched the query.
		'''
		return event


	def process(self, context, event):
		matched = self.Query.match(event)
		if matched:
			new_event = self.on_hit(context, event)
		else:
			new_event = self.on_miss(context, event)

		return new_event
