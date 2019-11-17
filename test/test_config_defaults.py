import inspect
import sys

import asab
from bspump import unittest


class TestConfigDefaults(unittest.TestCase):

	def test_default_value_is_not_none(self):
		to_inspect = []
		# For BSPump modules
		for _, module in inspect.getmembers(sys.modules['bspump'], inspect.ismodule):
			for _, klass in inspect.getmembers(module, inspect.isclass):
				if issubclass(klass, asab.ConfigObject):
					to_inspect.append(klass)

		# For BSPump classes
		for _, klass in inspect.getmembers(sys.modules['bspump'], inspect.isclass):
			if issubclass(klass, asab.ConfigObject):
				to_inspect.append(klass)

		# Make unique
		to_inspect = list(set(to_inspect))

		for klass in to_inspect:
			for key, value in klass.ConfigDefaults.items():
				self.assertIsNotNone(value, f"None found for key {key} in {klass}")

