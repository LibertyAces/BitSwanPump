from ...abc import Expression, evaluate


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

	def __init__(self, app, *, arg_with=None, arg_set=None, arg_modify=None, arg_del=None, arg_add=None, arg_update=None):
		super().__init__(app)

		self.With = arg_with

		if arg_set is not None:
			assert(isinstance(arg_set, dict))
		self.Set = arg_set

		if arg_modify is not None:
			assert(isinstance(arg_modify, dict))
		self.Modify = arg_modify

		if arg_add is not None:
			assert(isinstance(arg_add, dict))
		self.Add = arg_add

		if arg_del is not None:
			assert(isinstance(arg_del, list))
		self.Del = arg_del

		self.Update = arg_update


	def __call__(self, context, event, *args, **kwargs):
		if self.With is None:
			with_dict = dict()
		else:
			with_dict = evaluate(self.With, context, event, *args, **kwargs)
			# TODO: Must be usable as a dictionary

		if self.Set is not None:
			for key, value in self.Set.items():
				with_dict[key] = evaluate(value, context, event, *args, **kwargs)

		if self.Modify is not None:
			for key, value in self.Modify.items():
				try:
					orig = with_dict[key]
				except KeyError:
					continue
				with_dict[key] = evaluate(value, context, event, orig, *args, **kwargs)

		if self.Add is not None:
			for key, value in self.Add.items():
				with_dict[key] += evaluate(value, context, event, *args, **kwargs)

		if self.Update is not None:
			update_dict = evaluate(self.Update, context, event, *args, **kwargs)
			if update_dict is not None and update_dict is not False:
				with_dict.update(update_dict)

		if self.Del is not None:
			for key in self.Del:
				with_dict.pop(key, None)

		return with_dict
