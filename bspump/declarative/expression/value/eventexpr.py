from ...abc import Expression


class EVENT(Expression):
	"""
The current event.

Usage:
```
!EVENT
``
	"""

	def __init__(self, app, location, *, value):
		super().__init__(app, location)
		assert(value == "")

	def __call__(self, context, event, *args, **kwargs):
		return event


class KWARGS(Expression):
	"""
The current kwargs.

Usage:
```
!KWARGS
``
	"""

	def __init__(self, app, location, *, value):
		super().__init__(app, location)
		assert(value == "")

	def __call__(self, context, event, *args, **kwargs):
		return kwargs



class KWARG(Expression):
	"""
The item from a kwargs.

Usage:
```
!KWARG argname
``
	"""

	def __init__(self, app, location, *, value):
		super().__init__(app, location)
		self.ArgName = value

	def __call__(self, context, event, *args, **kwargs):
		return kwargs[self.ArgName]


class ARGS(Expression):
	def __init__(self, app, location, *, value):
		super().__init__(app, location)
		assert(value == '')

	def __call__(self, context, event, *args, **kwargs):
		return args


class ARG(Expression):
	def __init__(self, app, location, *, value):
		super().__init__(app, location)
		assert(value == '')
		self.ArgNumber = 0

	def __call__(self, context, event, *args, **kwargs):
		return args[self.ArgNumber]
