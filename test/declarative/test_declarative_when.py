import os

import bspump.declarative
import bspump.unittest


class TestDeclarativeWhen(bspump.unittest.TestCase):

	def setUp(self) -> None:
		super().setUp()
		self.Builder = bspump.declarative.ExpressionBuilder(self.App)


	def load(self, decl_fname):
		basedir = os.path.dirname(__file__)
		with open(os.path.join(basedir, decl_fname), 'r') as f:
			return self.Builder.parse(f.read())


	def test_when_01_else(self):
		decl = self.load('./test_when.yaml')
		res = decl({}, {'key': -1})
		self.assertEqual(res, "Unknown")

	def test_when_01_exact(self):
		decl = self.load('./test_when.yaml')
		res = decl({}, {'key': 34})
		self.assertEqual(res, "Thirty four")

	def test_when_01_range(self):
		decl = self.load('./test_when.yaml')
		res = decl({}, {'key': 45})
		self.assertEqual(res, "fourty to fifty (exclusive)")

	def test_when_01_set(self):
		decl = self.load('./test_when.yaml')
		res = decl({}, {'key': 75})
		self.assertEqual(res, "seventy five, seven, nine")
