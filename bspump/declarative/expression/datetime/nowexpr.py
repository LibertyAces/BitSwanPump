import time
from ...abc import Expression


class NOW(Expression):
	"""
	Unit test usage to mock current time:

		import time
		import unittest.mock

		class MetaTestCase(unittest.TestCase):

			@unittest.mock.patch('bspump.declarative.expression.NOW.Time')
			def runTest(self, mock_time):
				mock_time.return_value = 1234567890 # Mocked timestamp
				...
	"""

	Attributes = {}
	Time = time.time


	def __init__(self, app, *, value):
		super().__init__(app)
		assert(value == "")


	def __call__(self, context, event, *args, **kwargs):
		return self.Time()


	def get_outlet_type(self):
		return float.__name__
