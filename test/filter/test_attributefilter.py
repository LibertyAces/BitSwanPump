import bspump.filter
import bspump.unittest


class AttributeFilterWithAttributeFields(bspump.filter.AttributeFilter):
	def get_fields(self, event):
		return ["attribute"]


class UnpredictableAttributeFilter(bspump.filter.AttributeFilter):
	def predicate(self, event):
		return False


class TestAttributeFilter(bspump.unittest.ProcessorTestCase):

	def test_attribute_filter(self):
		events = [
			(None, {"attribute": "value"}),
		]
		self.set_up_processor(bspump.filter.AttributeFilter)

		output = self.execute(
			events
		)

		self.assertEqual(
			[event for context, event in output],
			[{"attribute": "value"}]
		)

	def test_test_attribute_filter_inclusive(self):
		events = [
			(None, {"attribute": "value"}),
		]
		self.set_up_processor(bspump.filter.AttributeFilter, inclusive=True)

		output = self.execute(
			events
		)

		self.assertEqual(
			[event for context, event in output],
			[{}]
		)

	def test_attribute_filter_with_fields(self):
		events = [
			(None, {"attribute": "value"}),
		]
		self.set_up_processor(AttributeFilterWithAttributeFields)

		output = self.execute(
			events
		)

		self.assertEqual(
			[event for context, event in output],
			[{}]
		)

	def test_attribute_filter_with_fields_inclusive(self):
		events = [
			(None, {"attribute": "value"}),
		]
		self.set_up_processor(AttributeFilterWithAttributeFields, inclusive=True)

		output = self.execute(
			events
		)

		self.assertEqual(
			[event for context, event in output],
			[{"attribute": "value"}]
		)

	def test_unpredictable_attribute_filter(self):
		events = [
			(None, {"attribute": "value"}),
		]
		self.set_up_processor(UnpredictableAttributeFilter)

		output = self.execute(
			events
		)

		self.assertEqual(
			[event for context, event in output],
			[{"attribute": "value"}]
		)

	def test_unpredictable_attribute_filter_inclusive(self):
		events = [
			(None, {"attribute": "value"}),
		]
		self.set_up_processor(UnpredictableAttributeFilter, inclusive=True)

		output = self.execute(
			events
		)

		self.assertEqual(
			[event for context, event in output],
			[{"attribute": "value"}]
		)
