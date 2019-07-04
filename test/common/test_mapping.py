from unittest.mock import MagicMock

import bspump.unittest
import bspump.common


class TestMappingKeysProcessor(bspump.unittest.ProcessorTestCase):

	def test_mapping_keys_processor(self):
		events = [
			(None, {'foo': 'bar'}),
			(None, {'fizz': 'buzz'}),
			(None, {'spam': 'eggs'}),
		]

		self.set_up_processor(bspump.common.MappingKeysProcessor)

		output = self.execute(
			events
		)

		self.assertEqual(
			[event for context, event in output],
			[['foo'], ['fizz'], ['spam']]
		)


class TestMappingValuesProcessor(bspump.unittest.ProcessorTestCase):

	def test_mapping_values_processor(self):
		events = [
			(None, {'foo': 'bar'}),
			(None, {'fizz': 'buzz'}),
			(None, {'spam': 'eggs'}),
		]

		self.set_up_processor(bspump.common.MappingValuesProcessor)

		output = self.execute(
			events
		)

		self.assertEqual(
			[event for context, event in output],
			[['bar'], ['buzz'], ['eggs']]
		)


class TestMappingItemsProcessor(bspump.unittest.ProcessorTestCase):

	def test_mapping_items_processor(self):
		events = [
			(None, {'foo': 'bar'}),
			(None, {'fizz': 'buzz'}),
			(None, {'spam': 'eggs'}),
		]

		self.set_up_processor(bspump.common.MappingItemsProcessor)

		output = self.execute(
			events
		)

		self.assertEqual(
			[event for context, event in output],
			[[('foo', 'bar')], [('fizz', 'buzz')], [('spam', 'eggs')]]
		)


class TestMappingKeysGenerator(bspump.unittest.ProcessorTestCase):

	def test_mapping_keys_generator(self):
		events = [
			(None, {'foo': 'bar'}),
			(None, {'fizz': 'buzz'}),
			(None, {'spam': 'eggs'}),
		]

		self.set_up_processor(bspump.common.MappingKeysGenerator)

		output = self.execute(
			events
		)

		self.assertEqual(
			[event for context, event in output],
			['foo', 'fizz', 'spam']
		)


class TestMappingValuesGenerator(bspump.unittest.ProcessorTestCase):

	def test_mapping_values_generator(self):
		events = [
			(None, {'foo': 'bar'}),
			(None, {'fizz': 'buzz'}),
			(None, {'spam': 'eggs'}),
		]

		self.set_up_processor(bspump.common.MappingValuesGenerator)

		output = self.execute(
			events
		)

		self.assertEqual(
			[event for context, event in output],
			['bar', 'buzz', 'eggs']
		)


class TestMappingItemsGenerator(bspump.unittest.ProcessorTestCase):

	def test_mapping_items_generator(self):
		events = [
			(None, {'foo': 'bar'}),
			(None, {'fizz': 'buzz'}),
			(None, {'spam': 'eggs'}),
		]

		self.set_up_processor(bspump.common.MappingItemsGenerator)

		output = self.execute(
			events
		)

		self.assertEqual(
			[event for context, event in output],
			[('foo', 'bar'), ('fizz', 'buzz'), ('spam', 'eggs')]
		)

