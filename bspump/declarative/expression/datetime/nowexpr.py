import datetime
from ...abc import Expression


class NOW(Expression):
	"""
	Unit test usage to mock current time:

		import datetime
		import bspump.declarative.expression
		import unittest.mock


		class MetaTestCase(unittest.TestCase):

			@unittest.mock.patch('bspump.declarative.expression.NOW.Datetime')
			def runTest(self, mock_datetime):
				mock_datetime.utcnow.return_value = datetime.datetime(2020, 5, 15) # Mocked date
				...
	"""

	Datetime = datetime.datetime

	def __init__(self, app, *, value):
		super().__init__(app)
		assert(value == "")

	def __call__(self, context, event, *args, **kwargs):
		return self.Datetime.utcnow().timestamp()
