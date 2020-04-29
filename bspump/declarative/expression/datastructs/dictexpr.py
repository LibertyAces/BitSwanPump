from ...abc import Expression


class DICT(Expression):
	"""
Create or update the dictionary.

```
!DICT
with: !EVENT
set:
	item1: foo
	item2: bar
	item3: ...
del:
	- item4

```

If `with` is not specified, the new dictionary will be created.
`add` is also optional.

This is how to create the empty dictionary:
```
!DICT {}
```
"""

	def __init__(self, app, *, arg_with=None, arg_set=None, arg_update=None, arg_del=None, arg_add=None):
		super().__init__(app)

		self.With = arg_with

		if arg_set is not None:
			assert(isinstance(arg_set, dict))
		self.Set = arg_set

		if arg_update is not None:
			assert(isinstance(arg_update, dict))
		self.Update = arg_update

		if arg_add is not None:
			assert(isinstance(arg_add, dict))
		self.Add = arg_add

		if arg_del is not None:
			assert(isinstance(arg_del, list))
		self.Del = arg_del

	def __call__(self, context, event, *args, **kwargs):
		if self.With is None:
			with_dict = dict()
		else:
			with_dict = self.evaluate(self.With, context, event, *args, **kwargs)
			# TODO: Must be usable as a dictionary

		if self.Set is not None:
			for key, value in self.Set.items():
				with_dict[key] = self.evaluate(value, context, event, *args, **kwargs)

		if self.Update is not None:
			for key, value in self.Update.items():
				try:
					orig = with_dict[key]
				except KeyError:
					continue
				with_dict[key] = self.evaluate(value, context, event, orig, *args, **kwargs)

		if self.Add is not None:
			for key, value in self.Add.items():
				with_dict[key] += self.evaluate(value, context, event, *args, **kwargs)

		if self.Del is not None:
			for key in self.Del:
				with_dict.pop(key, None)

		return with_dict
