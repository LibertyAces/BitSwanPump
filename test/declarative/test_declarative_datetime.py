import os
import datetime

import bspump.declarative
import bspump.unittest


class TestDeclarativeDateTime(bspump.unittest.TestCase):

	def setUp(self) -> None:
		super().setUp()
		self.Builder = bspump.declarative.ExpressionBuilder(self.App)


	def load(self, decl_fname):
		basedir = os.path.dirname(__file__)
		with open(os.path.join(basedir, decl_fname), 'r') as f:
			return self.Builder.parse(f.read())[0]


	def test_datetime_parse_set_year(self):
		decl = self.load('./test_datetime_parse_set_year.yaml')

		res = decl({}, {}, "Mar 16 07:46:24")
		now = datetime.datetime.now()
		dt = datetime.datetime(year=now.year, month=3, day=16, hour=7, minute=46, second=24, tzinfo=datetime.timezone.utc)
		self.assertEqual(res, dt.timestamp())


	def test_datetime_parse_timezone(self):
		decl = self.load('./test_datetime_parse_timezone.yaml')

		res = decl({}, {})
		self.assertEqual(res, 946681200.0)


	def test_datetime_parse_add(self):
		decl = self.load('./test_datetime_add.yaml')

		res = decl({}, {})
		self.assertEqual(res, 2.0)


	def test_datetime_parse_failed(self):
		decl = self.load('./test_datetime_parse_fail.yaml')

		res = decl({}, {})
		self.assertEqual(res, 'Failed :-(')


	def test_datetime_parse_tz(self):
		decl = self.load('./test_datetime_parse_tz.yaml')

		res = decl({}, {})
		self.assertEqual(res, 1585621784.0)
