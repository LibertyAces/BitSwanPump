import re

from ...abc import Expression
from ..value.valueexpr import VALUE


class REGEX(Expression):
	"""
	Checks if `value` matches with the `regex`, returns `hit` / `miss` respectively.
	"""

	Attributes = {
		"Value": ["*"],  # TODO: This ...
		"Regex": ["*"],  # TODO: This ...
		"Hit": ["*"],
		"Miss": ["*"],
	}

	Category = "Regex"


	def __init__(self, app, *, arg_regex, arg_what, arg_hit=True, arg_miss=False):
		super().__init__(app)
		self.Value = arg_what
		self.Regex = re.compile(arg_regex)

		if not isinstance(arg_hit, Expression):
			self.Hit = VALUE(app, value=arg_hit)
		else:
			self.Hit = arg_hit

		if not isinstance(arg_miss, Expression):
			self.Miss = VALUE(app, value=arg_miss)
		else:
			self.Miss = arg_miss

		# TODO: Regex flags

	def __call__(self, context, event, *args, **kwargs):
		value = self.Value(context, event, *args, **kwargs)
		match = re.search(self.Regex, value)
		if match is None:
			return self.Miss(context, event, *args, **kwargs)
		else:
			return self.Hit(context, event, *args, **kwargs)


class REGEX_PARSE(Expression):
	"""
	Search `value` forr `regex` with regular expressions groups.
	If nothing is found `miss` is returned.
	Otherwise, groups are returned in as a list.

	If `fields` are provided, the groups are mapped to provided fields.
	"""

	Attributes = {
		"Value": ["*"],  # TODO: This ...
		"Regex": ["*"],  # TODO: This ...
		"Unset": [],
		"Update": ["*"],
		"Items": [],
	}

	Category = "Regex"


	def __init__(self, app, *, arg_regex, arg_what, arg_items=None, arg_miss=None, arg_set=None, arg_unset=None, arg_update=None):
		super().__init__(app)

		if not isinstance(arg_what, Expression):
			self.Value = VALUE(app, value=arg_what)
		else:
			self.Value = arg_what

		self.Regex = re.compile(arg_regex)
		self.Items = arg_items

		if not isinstance(arg_miss, Expression):
			self.Miss = VALUE(app, value=arg_miss)
		else:
			self.Miss = arg_miss

		self.ArgSet = arg_set
		self.Set = None

		if arg_unset is not None:
			assert(isinstance(arg_unset, list))
		self.Unset = arg_unset

		self.Update = arg_update

		# TODO: Regex flags

	def set(self, key, value):
		setattr(self, key, value)

		if "Set" in key:
			self.Set[key[3:]] = value

	def initialize(self):
		if self.ArgSet is None:
			self.Set = None
		else:
			assert(isinstance(self.ArgSet, dict))
			self.Set = dict()
			self._set_value_or_expression_to_attribute(self.ArgSet, self.Set, "Set")

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
		value = self.Value(context, event, *args, **kwargs)
		try:
			match = re.search(self.Regex, value)
		except TypeError:
			match = None
		if match is None:
			return self.Miss(context, event, *args, **kwargs)

		groups = match.groups()
		if self.Items is None:
			return groups

		ret = dict()
		for item, group in zip(self.Items, groups):
			if isinstance(item, Expression):
				result = item(context, event, group, *args, **kwargs)
				if result is None:
					return self.Miss(context, event, *args, **kwargs)
				ret[result] = group

			elif isinstance(item, dict):
				if group is None:
					continue
				assert(len(item) == 1)

				key, value = next(iter(item.items()))

				if isinstance(value, Expression):
					v = value(context, event, group, *args, **kwargs)
					if v is not None:
						ret[key] = v

				elif isinstance(value, list):
					for valuei in value:
						v = valuei(context, event, group, *args, **kwargs)
						if v is not None:
							ret[key] = v
							break

				else:
					raise RuntimeError("Unexpected type: '{}'".format(value))
			else:
				ret[item] = group

		if self.Set is not None:
			for key, value in self.Set.items():
				v = value(context, event, ret, *args, **kwargs)
				if v is not None:
					ret[key] = v

		if self.Update is not None:
			update_dict = self.Update(context, event, ret, *args, **kwargs)
			if update_dict is not None and update_dict is not False:
				ret.update(update_dict)

		if self.Unset is not None:
			for key in self.Unset:
				ret.pop(key, None)

		return ret


class REGEX_REPLACE(Expression):
	"""
	Search `regex` in `value` and replace with `replace`.

	See Python documentation of `re.sub()` for more details.
	"""

	Attributes = {
		"Value": ["*"],  # TODO: This ...
		"Regex": ["*"],  # TODO: This ...
		"Replace": ["*"],
	}

	Category = "Regex"


	def __init__(self, app, *, arg_regex, arg_replace, arg_what):
		super().__init__(app)
		self.Value = arg_what
		self.Regex = re.compile(arg_regex)

		if not isinstance(arg_replace, Expression):
			self.Replace = VALUE(app, value=arg_replace)
		else:
			self.Replace = arg_replace

	def __call__(self, context, event, *args, **kwargs):
		value = self.Value(context, event, *args, **kwargs)
		repl = self.Replace(context, event, *args, **kwargs)
		return self.Regex.sub(repl, value)


class REGEX_SPLIT(Expression):

	Attributes = {
		"Value": ["*"],  # TODO: This ...
		"Regex": ["*"],  # TODO: This ...
		"Max": ["*"],
	}

	Category = "Regex"


	def __init__(self, app, *, arg_regex, arg_what, arg_max=0):
		super().__init__(app)
		self.Value = arg_what
		self.Regex = re.compile(arg_regex)

		if not isinstance(arg_max, Expression):
			self.Max = VALUE(app, value=arg_max)
		else:
			self.Max = arg_max

	def __call__(self, context, event, *args, **kwargs):
		value = self.Value(context, event, *args, **kwargs)
		maxsplit = self.Max(context, event, *args, **kwargs)
		return self.Regex.split(value, maxsplit=maxsplit)


class REGEX_FINDALL(Expression):

	Attributes = {
		"Value": ["*"],  # TODO: This ...
		"Regex": ["*"],  # TODO: This ...
	}

	Category = "Regex"


	def __init__(self, app, *, arg_regex, arg_what):
		super().__init__(app)
		self.Value = arg_what
		self.Regex = re.compile(arg_regex)

	def __call__(self, context, event, *args, **kwargs):
		value = self.Value(context, event, *args, **kwargs)
		return self.Regex.findall(value)
