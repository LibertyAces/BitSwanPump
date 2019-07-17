import mongoquery

import bspump.filter
import bspump.unittest


class ContentFilterOnHitPassOnly(bspump.filter.ContentFilter):
	def on_hit(self, context, event):
		return event

	def on_miss(self, context, event):
		return None


class TestContentFilter(bspump.unittest.ProcessorTestCase):

	def test_content_filter(self):
		events = [
			(None, {"foo": "bar"}),
			(None, {"fizz": "buzz"}),
		]
		self.set_up_processor(bspump.filter.ContentFilter)

		output = self.execute(
			events
		)

		self.assertEqual(
			[event for context, event in output],
			[{"foo": "bar"}, {"fizz": "buzz"}]
		)

	def test_content_filter_with_query(self):
		events = [
			(None, {"foo": "bar"}),
			(None, {"fizz": "buzz"}),
		]
		self.set_up_processor(bspump.filter.ContentFilter, query={"foo": "bar"})

		output = self.execute(
			events
		)

		self.assertEqual(
			[event for context, event in output],
			[{"foo": "bar"}, {"fizz": "buzz"}]
		)

	def test_custom_content_filter_with_query(self):
		events = [
			(None, {"foo": "bar"}),
			(None, {"fizz": "buzz"}),
		]
		self.set_up_processor(ContentFilterOnHitPassOnly, query={"foo": "bar"})

		output = self.execute(
			events
		)

		self.assertEqual(
			[event for context, event in output],
			[{"foo": "bar"}]
		)

	def test_content_filter_with_invalid_query(self):
		with self.assertRaises(mongoquery.QueryError):
			self.set_up_processor(bspump.filter.ContentFilter, query={"$foo": 2})

		with self.assertRaises(TypeError):
			self.set_up_processor(bspump.filter.ContentFilter, query={"foo": {"$in": None}})

