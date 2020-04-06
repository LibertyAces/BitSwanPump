from ...abc import Expression


class EVENT(Expression):
	"""
The current event.

Usage:
```
!EVENT
``
	"""

	def __init__(self, app, *, value):
		super().__init__(app)
		assert(value == "")

	def __call__(self, context, event, *args, **kwargs):
		return event


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
