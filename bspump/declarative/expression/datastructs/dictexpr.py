from ...abc import Expression, evaluate

import logging

#

L = logging.getLogger(__name__)

#


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

	def __init__(self, app, *, arg_with=None, arg_set=None, arg_modify=None, arg_unset=None, arg_add=None, arg_update=None, arg_mandatory=None):
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

		if arg_unset is not None:
			assert(isinstance(arg_unset, list))
		self.Unset = arg_unset

		if arg_mandatory is not None:
			assert(isinstance(arg_mandatory, list))
		self.Mandatory = arg_mandatory

		self.Update = arg_update


	def __call__(self, context, event, *args, **kwargs):
		if self.With is None:
			with_dict = dict()
		else:
			with_dict = evaluate(self.With, context, event, *args, **kwargs)
			if with_dict is None:
				return None
			# TODO: Must be usable as a dictionary

		if self.Set is not None:
			for key, value in self.Set.items():
				v = evaluate(value, context, event, *args, **kwargs)
				if v is not None:
					with_dict[key] = v

		if self.Modify is not None:
			for key, value in self.Modify.items():
				try:
					orig = with_dict[key]
				except KeyError:
					continue
				with_dict[key] = evaluate(value, context, event, orig, *args, **kwargs)

		if self.Add is not None:
			for key, value in self.Add.items():
				v = evaluate(value, context, event, *args, **kwargs)
				if v is not None:
					with_dict[key] += v

		if self.Update is not None:
			update_dict = evaluate(self.Update, context, event, with_dict, *args, **kwargs)
			if update_dict is not None and update_dict is not False:
				with_dict.update(update_dict)

		if self.Unset is not None:
			for key in self.Unset:
				with_dict.pop(key, None)

		# Check that all mandatory fields are present in the dictionary
		if self.Mandatory is not None:
			for mandatory_field in self.Mandatory:
				if mandatory_field not in with_dict:
					L.error("Mandatory field '{}' not present in dictionary. Returning None.".format(mandatory_field))
					return None

		return with_dict
