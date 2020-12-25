import os

import bspump.declarative
import bspump.unittest


class TestDeclarativeJoin(bspump.unittest.TestCase):

	def setUp(self) -> None:
		super().setUp()
		self.Builder = bspump.declarative.ExpressionBuilder(self.App)


	def load(self, decl_fname):
		basedir = os.path.dirname(__file__)
		with open(os.path.join(basedir, decl_fname), 'r') as f:
			return self.Builder.parse(f.read())


	def test_join_01(self):
		event = {
			'string': "STRING",
			'integer': 15,
		}

		decl = self.load('./test_join_01.yaml')

		res = decl({}, event)
		self.assertEqual(res, "STRING:15:")



	def test_join_02(self):
		event = {
			'string': "STRING",
			'integer': 15,
		}

		decl = self.load('./test_join_02.yaml')

		res = decl({}, event)
		self.assertEqual(res, None)

