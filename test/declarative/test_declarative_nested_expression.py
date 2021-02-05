import os

import bspump.declarative
import bspump.unittest


class TestDeclarativeNestedExpression(bspump.unittest.TestCase):

	def setUp(self) -> None:
		super().setUp()
		self.Builder = bspump.declarative.ExpressionBuilder(self.App)
		self.Optimizer = bspump.declarative.ExpressionOptimizer(self.App)


	def load(self, decl_fname):
		basedir = os.path.dirname(__file__)
		with open(os.path.join(basedir, decl_fname), 'r') as f:
			return self.Builder.parse(f.read())[0]


	def test_01(self):
		decl = self.load('./test_declarative_nested_expression.yaml')

		event = {
			"continue": "yes",
		}

		res_predicate = self.Optimizer.optimize(decl["predicate"])({}, event)
		res_parse = decl["parse"]({}, event)

		self.assertEqual(res_predicate, True)

		self.assertEqual(res_parse, {
			"name": "Parse Dict Success",
		})


	def test_02(self):
		decl = self.load('./test_declarative_nested_expression.yaml')

		event = {
			"continue": "yes",
		}

		context = {
			"brain": {
				"idea": "This is beautiful parsing."
			}
		}
		res_parse = self.Optimizer.optimize(decl["parse"])(context, event)

		self.assertEqual(res_parse, {
			"name": "Parse Dict Success",
			"idea": "This is beautiful parsing.",
		})


	def test_03(self):
		"""
		Test JOIN expression initialization
		:return:
		"""

		decl = self.load('./test_declarative_nested_expression.yaml')

		res_parse = self.Optimizer.optimize(decl["join"])({}, "Prema")

		self.assertEqual(res_parse, {
			"name": "Prema",
			"message": "Prema is nice!",
		})
