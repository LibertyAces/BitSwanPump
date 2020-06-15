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


	def test_regex_parse_02(self):
		decl = self.load('./test_regex_parse_02.yaml')

		res = decl({}, {})
		self.assertEqual(res, {
			'.tmp14': '6620',
			'.tmp15': '2388',
			'.tmp16': '137.124453',
			'act': 'ACCEPTED',
			'app': 'https',
			'cs1': 'FAILED',
			'cs2': 'EXT-OWA-OK',
			'deviceExternalId': 'TCPP-888',
			'dhost': '192.168.24.1',
			'dpt': 443,
			'dst': '192.168.24.1',
			'duser': '<NULL>',
			'in': 6620,
			'out': 2388,
			'proto': 'TCP',
			'severity': 'I',
			'shost': '52.125.141.18',
			'spt': 35822,
			'src': '52.125.141.18'
		})
