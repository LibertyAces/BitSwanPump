from ...abc import Expression
from ..value.valueexpr import VALUE
from ...declerror import DeclarationError

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
unset:
	- item4

```

If `with` is not specified, the new dictionary will be created.
`add` is also optional.

This is how to create the empty dictionary:
```
!DICT {}
```
"""

	Attributes = {
		"With": ["*"],  # TODO: This ...
		"Update": ["*"],  # TODO: This ...
		"Mandatory": [],  # TODO: This ...
		"Unset": [],  # TODO: This ...
	}

	def __init__(self, app, *, arg_with=None, arg_set=None, arg_modify=None, arg_unset=None, arg_add=None, arg_update=None, arg_mandatory=None, arg_flatten=None):
		super().__init__(app)

		self.With = arg_with

		self.ArgSet = arg_set
		self.ArgFlatten = arg_flatten
		self.ArgModify = arg_modify
		self.ArgAdd = arg_add
		self.Set = None
		self.Flatten = None
		self.Modify = None
		self.Add = None

		self.Unset = arg_unset
		self.Mandatory = arg_mandatory
		self.Update = arg_update

	def set(self, key, value):
		setattr(self, key, value)

		if "Set" in key:
			self.Set[key[3:]] = value
		if "Flatten" in key:
			self.Flatten[key[7:]] = value
		if "Add" in key:
			self.Add[key[3:]] = value
		if "Modify" in key:
			self.Modify[key[6:]] = value

	def initialize(self):
		if self.ArgSet is None:
			self.Set = None
		else:
			assert isinstance(self.ArgSet, dict)
			self.Set = dict()
			self._set_value_or_expression_to_attribute(self.ArgSet, self.Set, "Set")

		if self.ArgFlatten is None:
			self.Flatten = None
		else:
			assert isinstance(self.ArgFlatten, dict)
			self.Flatten = dict()
			self._set_value_or_expression_to_attribute(self.ArgFlatten, self.Flatten, "Flatten")

		if self.ArgModify is None:
			self.Modify = None
		else:
			assert isinstance(self.ArgModify, dict)
			self.Modify = dict()
			self._set_value_or_expression_to_attribute(self.ArgModify, self.Modify, "Modify")

		if self.ArgAdd is None:
			self.Add = None
		else:
			assert isinstance(self.ArgAdd, dict)
			self.Add = dict()
			self._set_value_or_expression_to_attribute(self.ArgAdd, self.Add, "Add")

	def _set_value_or_expression_to_attribute(self, _from, _to, name):
		for key, value in _from.items():

			# Parse value to attribute, if not expression
			if isinstance(value, Expression):
				_to[key] = value
			else:
				assert isinstance(value, (int, str, bytes, bool, tuple, list)) or value is None
				value = VALUE(self.App, value=value)
				_to[key] = value

			# Set the value to the class attribute
			attr_name = '{}{}'.format(name, key)
			setattr(self, attr_name, value)
			self.Attributes[attr_name] = value.get_outlet_type()

	def __call__(self, context, event, *args, **kwargs):

		try:

			if self.With is None:
				with_dict = dict()
			else:
				with_dict = self.With(context, event, *args, **kwargs)
				if with_dict is None:
					return None
				# TODO: Must be usable as a dictionary

			if self.Set is not None:
				for key, value in self.Set.items():
					v = value(context, event, *args, **kwargs)
					if v is not None:
						with_dict[key] = v

			if self.Flatten is not None:
				for key, value in self.Flatten.items():
					v = value(context, event, *args, **kwargs)
					if v is not None and isinstance(v, list):
						for el in v:
							with_dict[key + '.' + el["Name"]] = el["Value"]
			if self.Modify is not None:
				for key, value in self.Modify.items():
					# Obtain the original value and pass it to the modify expression
					orig = with_dict.pop(key, None)

					modified_value = value(context, event, orig, *args, **kwargs)

					# Only if modification is successful, store it
					# Unsetting values should be done via unset
					if modified_value is not None:
						with_dict[key] = modified_value

			if self.Add is not None:
				for key, value in self.Add.items():
					v = value(context, event, *args, **kwargs)
					if v is not None:
						try:
							with_dict[key] += v
						except KeyError:
							continue

			if self.Update is not None:
				update_dict = self.Update(context, event, with_dict, *args, **kwargs)
				if update_dict is not None and update_dict is not False:
					try:
						with_dict.update(update_dict)
					except TypeError:
						pass

			if self.Unset is not None:
				for key in self.Unset:
					popped = with_dict.pop(key, None)

			# Check that all mandatory fields are present in the dictionary
			if self.Mandatory is not None:
				for mandatory_field in self.Mandatory:
					if mandatory_field not in with_dict:
						# TODO: Remove eventually when there are more occurrences among other expressions as well
						L.warning("Mandatory field '{}' not present in dictionary. Returning None.".format(mandatory_field))
						return None

			return with_dict

		except Exception as e:
			raise DeclarationError(original_exception=e, location=self.get_location())
