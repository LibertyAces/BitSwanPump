import os

import bspump.declarative
import bspump.unittest


class TestDeclarativeRegex(bspump.unittest.TestCase):

	def setUp(self) -> None:
		super().setUp()
		self.Builder = bspump.declarative.ExpressionBuilder(self.App)


	def load(self, decl_fname):
		basedir = os.path.dirname(__file__)
		with open(os.path.join(basedir, decl_fname), 'r') as f:
			return self.Builder.parse(f.read())


	def test_regex_parse_01(self):
		decl = self.load('./test_regex_parse_01.yaml')

		res = decl({}, {})

		self.assertEqual(res, {
			'first': 'foo',
			'second': '123',
			'third': 'bar with postfix',
			'item1': 'foo',
		})
