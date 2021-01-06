from ...abc import Expression, evaluate


class CONTEXT(Expression):
	"""
The current context.

Usage:
```
!CONTEXT
``
	"""

	Attributes = {
	}

	def __init__(self, app, *, value):
		super().__init__(app)
		assert(value == "")

	def __call__(self, context, event, *args, **kwargs):
		return context


class CONTEXT_SET(Expression):

	Attributes = {
		"What": ["*"],  # TODO: This ...
		"Set": ["*"],  # TODO: This ...
	}

	def __init__(self, app, *, arg_set, arg_what=None):
		super().__init__(app)
		self.What = arg_what
		self.Set = arg_set

	def __call__(self, context, event, *args, **kwargs):
		if self.Set is not None:
			for key, value in self.Set.items():
				v = evaluate(value, context, event, *args, **kwargs)
				if v is not None:
					context[key] = v

		return evaluate(self.What, context, event, *args, **kwargs)
