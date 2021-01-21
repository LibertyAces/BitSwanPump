import os

import bspump.declarative
import bspump.unittest


class TestDeclarativeDictParser(bspump.unittest.TestCase):

	def setUp(self) -> None:
		super().setUp()
		self.Builder = bspump.declarative.ExpressionBuilder(self.App)


	def load(self, decl_fname):
		basedir = os.path.dirname(__file__)
		with open(os.path.join(basedir, decl_fname), 'r') as f:
			return self.Builder.parse(f.read())[0]


	def test_dict_parse_kvs_01(self):
		decl = self.load('./test_dict_parse_kvs_01.yaml')
		res = decl({},
			"""key1=value1 key2=value2 request=http://www.pandora.com/json/music/artist/justin-moore?explicit\\=false uri=3DLoiRDsBABCAA9FvE1htRg\\=\\="""
		)
		self.assertEqual(res, {
			'key1': 'value1',
			'key2': 'value2',
			'request': 'http://www.pandora.com/json/music/artist/justin-moore?explicit\\=false',
			'uri': '3DLoiRDsBABCAA9FvE1htRg\\=\\='
		})



	def test_dict_parse_kvdqs_01(self):
		decl = self.load('./test_dict_parse_kvdqs_01.yaml')
		res = decl({},
			'''key1="value1" key2="value2" key3="ssss\"aaa" request="http://www.pandora.com/json/music/artist/justin-moore?explicit\\=false"'''
		)
		self.assertEqual(res, {
			'key1': 'value1',
			'key2': 'value2',
			'key3': 'ssss"aaa',
			'request': 'http://www.pandora.com/json/music/artist/justin-moore?explicit\\=false',
		})


	def test_dict_parse_qs_01(self):
		decl = self.load('./test_dict_parse_qs_01.yaml')
		res = decl({},
			'''first=this+is+a+field&second=was+it+clear+%28already%29%3F'''
		)
		self.assertEqual(res, {
			'first': 'this is a field',
			'second': 'was it clear (already)?'
		})
