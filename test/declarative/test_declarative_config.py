import os

import bspump.declarative
import bspump.unittest


class TestDeclarativeConfig(bspump.unittest.TestCase):

	def setUp(self) -> None:
		super().setUp()
		self.Builder = bspump.declarative.ExpressionBuilder(self.App)


	def load(self, decl_fname):
		basedir = os.path.dirname(__file__)
		with open(os.path.join(basedir, decl_fname), 'r') as f:
			return self.Builder.parse(f.read())[0]


	def test_config_01(self):
		self.Builder.Config['item1'] = "foo"

		decl = self.load('./test_config_01.yaml')

		res = decl({}, {})
		self.assertEqual(res, ">foo<")
