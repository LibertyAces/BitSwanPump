from ...abc import Expression


class CONTEXT(Expression):
	"""
The current context.

Usage:
```
!CONTEXT
``
	"""

	def __init__(self, app, *, value):
		super().__init__(app)
		assert(value == "")

	def __call__(self, context, event, *args, **kwargs):
		return context



class CONTEXT_SET(Expression):

	def __init__(self, app, *, arg_set, arg_what=None):
		super().__init__(app)
		self.What = arg_what
		self.Set = arg_set

	def __call__(self, context, event, *args, **kwargs):
		if self.Set is not None:
			for key, value in self.Set.items():
				v = self.evaluate(value, context, event, *args, **kwargs)
				if v is not None:
					context[key] = v

		return self.evaluate(self.What, context, event, *args, **kwargs)
