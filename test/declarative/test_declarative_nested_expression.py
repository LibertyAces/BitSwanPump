import os

import bspump.declarative
import bspump.unittest


class TestDeclarativeNestedExpression(bspump.unittest.TestCase):

	def setUp(self) -> None:
		super().setUp()
		self.Builder = bspump.declarative.ExpressionBuilder(self.App)


	def load(self, decl_fname):
		basedir = os.path.dirname(__file__)
		with open(os.path.join(basedir, decl_fname), 'r') as f:
			return self.Builder.parse(f.read())[0]


	def test_01(self):
		decl = self.load('./test_declarative_nested_expression.yaml')

		event = {
			"continue": "yes",
		}

		res_predicate = decl["predicate"]({}, event)
		res_parse = decl["parse"]({}, event)

		self.assertEqual(res_predicate, True)

		self.assertEqual(res_parse, {
			"name": "Parse Dict Success"
		})
