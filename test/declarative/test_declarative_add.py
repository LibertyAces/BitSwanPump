import os

import bspump.declarative
import bspump.unittest


class TestDeclarativeAdd(bspump.unittest.TestCase):

	def setUp(self) -> None:
		super().setUp()
		self.Builder = bspump.declarative.ExpressionBuilder(self.App)


	def load(self, decl_fname):
		basedir = os.path.dirname(__file__)
		with open(os.path.join(basedir, decl_fname), 'r') as f:
			return self.Builder.parse(f.read())[0]



	def test_add_01(self):
		event = {
			'string1': "STRING1",
			'string2': "STRING2",
		}

		decl = self.load('./test_add_01.yaml')

		res = decl({}, event)
		self.assertEqual(res, "STRING1STRING2")


	def test_add_02(self):
		decl = self.load('./test_add_02.yaml')

		res = decl({}, {})
		self.assertEqual(res, 3)

		bspump.declarative.declaration_to_dot(decl, './test_add_02.dot')
