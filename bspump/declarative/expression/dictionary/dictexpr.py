from ...abc import Expression


class DICT(Expression):
	"""
Create or update the dictionary.

```
!DICT
with: !EVENT
add:
  item1: foo
  item2: bar
  item3: ...
```

If `with` is not specified, the new dictionary will be created.
`add` is also optional.

This is how to create the empty dictionary:
```
!DICT {}
```
    """


	def __init__(self, app, *, arg_add=None, arg_with=None):
		super().__init__(app)

		self.With = arg_with
		self.Add = arg_add


	def __call__(self, context, event, *args, **kwargs):
		if self.With is None:
			updated_dict = dict()
		else:
			updated_dict = self.evaluate(self.With, context, event, *args, **kwargs)

		if self.Add is not None:
			for key, value in self.Add.items():
				updated_dict[key] = self.evaluate(value, context, event, *args, **kwargs)

		return updated_dict
