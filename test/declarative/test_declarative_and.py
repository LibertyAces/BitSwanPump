import os

import bspump.declarative
import bspump.unittest


class TestDeclarativeAnd(bspump.unittest.TestCase):

	def setUp(self) -> None:
		super().setUp()
		self.Builder = bspump.declarative.ExpressionBuilder(self.App)


	def load(self, decl_fname):
		basedir = os.path.dirname(__file__)
		with open(os.path.join(basedir, decl_fname), 'r') as f:
			return self.Builder.parse(f.read())[0]


	def test_dict_01(self):
		decl = self.load('./test_and_01.yaml')

		bspump.declarative.declaration_to_dot(decl, './test_and_01.dot')
