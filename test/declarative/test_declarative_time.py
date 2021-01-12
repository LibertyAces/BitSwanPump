import os
import time

import bspump.declarative
import bspump.unittest


class TestDeclarativeTime(bspump.unittest.TestCase):

	def setUp(self) -> None:
		super().setUp()
		self.Builder = bspump.declarative.ExpressionBuilder(self.App)


	def load(self, decl_fname):
		basedir = os.path.dirname(__file__)
		with open(os.path.join(basedir, decl_fname), 'r') as f:
			return self.Builder.parse(f.read())[0]


	def test_now_01(self):
		t1 = time.time()

		decl = self.load('./test_now.yaml')
		res = decl({}, {})

		self.assertTrue(res >= t1)
		self.assertTrue(res <= time.time())
