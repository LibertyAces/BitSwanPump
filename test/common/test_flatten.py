import bspump.unittest
import bspump.common


class TestFlattenDictProcessor(bspump.unittest.ProcessorTestCase):
	def test_flatten_dict_processor(self):
		events = [
			(None, {
				"person": {
					"details": {
						"first_name": "John",
						"last_name": "Wick",
					},
					"address": {
						"city": "Mill Neck",
						"county": "USA",
					}
				}
			}),
			(None, {}),
		]

		self.set_up_processor(bspump.common.FlattenDictProcessor)

		output = self.execute(
			events
		)

		self.assertEqual(
			sorted([event for context, event in output], key=lambda x: len(x.keys())),
			[{
				None: {},
			}, {
				'person.details.first_name': 'John',
				'person.details.last_name': 'Wick',
				'person.address.city': 'Mill Neck',
				'person.address.county': 'USA',
			}]
		)
