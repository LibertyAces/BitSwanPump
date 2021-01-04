from ...abc import Expression


class EVENT(Expression):
	"""
The current event.

Usage:
```
!EVENT
``
	"""

	Attributes = {}

	def __init__(self, app, *, value):
		super().__init__(app)
		assert(value == "")

	def __call__(self, context, event, *args, **kwargs):
		return event

	def get_output_type(self):
		return dict.__name__


class KWARGS(Expression):
	"""
The current kwargs.

Usage:
```
!KWARGS
``
	"""

	Attributes = {}

	def __init__(self, app, *, value):
		super().__init__(app)
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

	def __init__(self, app, *, value):
		super().__init__(app)
		self.ArgName = value

	def __call__(self, context, event, *args, **kwargs):
		return kwargs[self.ArgName]


class ARGS(Expression):

	Attributes = {}

	def __init__(self, app, *, value):
		super().__init__(app)
		assert(value == '')

	def __call__(self, context, event, *args, **kwargs):
		return args


class ARG(Expression):

	Attributes = {}

	def __init__(self, app, *, value):
		super().__init__(app)
		assert(value == '')
		self.ArgNumber = 0

	def __call__(self, context, event, *args, **kwargs):
		return args[self.ArgNumber]
