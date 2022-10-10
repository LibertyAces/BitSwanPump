import os

import bspump.declarative
import bspump.unittest


class TestDeclarativeDict(bspump.unittest.TestCase):

	def setUp(self) -> None:
		super().setUp()
		self.Builder = bspump.declarative.ExpressionBuilder(self.App)
		self.Optimizer = bspump.declarative.ExpressionOptimizer(self.App)

	def load(self, decl_fname):
		basedir = os.path.dirname(__file__)
		with open(os.path.join(basedir, decl_fname), 'r') as f:
			return self.Builder.parse(f.read())[0]


	def test_dict_01(self):
		event = {
			'string': "STRING",
			'integer': 15,
		}

		decl = self.load('./test_dict_01.yaml')

		res = decl({}, event)
		self.assertEqual(res, {'item1': 'STRING', 'item2': 15})


	def test_dict_02(self):
		context = {
			"JSON": {
				"EndTime": "Tomorrow",
				"DeviceProperties": [
					{
						"Name": "OS",
						"Value": "Windows 10"
					},
					{
						"Name": "BrowserType",
						"Value": "Chrome"
					},
					{
						"Name": "IsCompliantAndManaged",
						"Value": "False"
					}
				]
			}
		}

		decl = self.load('./test_dict_02.yaml')

		res = self.Optimizer.optimize(decl)(context, {})

		self.assertEqual(res, {
			'o365.audit.EndTime': 'Tomorrow',
			'o365.audit.DeviceProperties.OS': 'Windows 10',
			'o365.audit.DeviceProperties.BrowserType': 'Chrome',
			'o365.audit.DeviceProperties.IsCompliantAndManaged': 'False'
			}
		)
