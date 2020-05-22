import os

import bspump.declarative
import bspump.unittest


class TestDeclarativeDict(bspump.unittest.TestCase):

	def setUp(self) -> None:
		super().setUp()
		self.Builder = bspump.declarative.ExpressionBuilder(self.App)


	def load(self, decl_fname):
		basedir = os.path.dirname(__file__)
		with open(os.path.join(basedir, decl_fname), 'r') as f:
			return self.Builder.parse(f.read())


	def test_dict_01(self):
		event = {
			'string': "STRING",
			'integer': 15,
		}

		decl = self.load('./test_dict_01.yaml')

		res = decl({}, event)
		self.assertEqual(res, {'item1': 'STRING', 'item2': 15})
