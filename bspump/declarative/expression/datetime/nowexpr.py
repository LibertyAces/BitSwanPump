import datetime
from ...abc import Expression

class NOW(Expression):

	def __init__(self, app, *, value):
		super().__init__(app)
		assert(value == "")

	def __call__(self, context, event, *args, **kwargs):
		return datetime.datetime.utcnow()
