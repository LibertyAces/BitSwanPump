import re

from ...abc import Expression, evaluate


class REGEX(Expression):
	"""
	Checks if `value` matches with the `regex`, returns `hit` / `miss` respectively.
	"""

	def __init__(self, app, location, *, arg_regex, arg_what, arg_hit=True, arg_miss=False):
		super().__init__(app, location)
		self.Value = arg_what
		self.Regex = re.compile(arg_regex)
		self.Hit = arg_hit
		self.Miss = arg_miss
		# TODO: Regex flags

	def __call__(self, context, event, *args, **kwargs):
		value = evaluate(self.Value, context, event, *args, **kwargs)
		match = re.search(self.Regex, value)
		if match is None:
			return evaluate(self.Miss, context, event, *args, **kwargs)
		else:
			return evaluate(self.Hit, context, event, *args, **kwargs)


class REGEX_PARSE(Expression):
	"""
	Search `value` forr `regex` with regular expressions groups.
	If nothing is found `miss` is returned.
	Otherwise, groups are returned in as a list.

	If `fields` are provided, the groups are mapped to provided fields.
	"""

	def __init__(self, app, location, *, arg_regex, arg_what, arg_items=None, arg_miss=None, arg_set=None, arg_unset=None, arg_update=None):
		super().__init__(app, location)
		self.Value = arg_what
		self.Regex = re.compile(arg_regex)
		self.Miss = arg_miss
		self.Items = arg_items

		if arg_set is not None:
			assert(isinstance(arg_set, dict))
		self.Set = arg_set

		if arg_unset is not None:
			assert(isinstance(arg_unset, list))
		self.Unset = arg_unset

		self.Update = arg_update

		# TODO: Regex flags


	def __call__(self, context, event, *args, **kwargs):
		value = evaluate(self.Value, context, event, *args, **kwargs)
		try:
			match = re.search(self.Regex, value)
		except TypeError:
			match = None
		if match is None:
			return evaluate(self.Miss, context, event, *args, **kwargs)

		groups = match.groups()
		if self.Items is None:
			return groups

		ret = dict()
		for item, group in zip(self.Items, groups):
			if isinstance(item, Expression):
				result = evaluate(item, context, event, group, *args, **kwargs)
				if result is None:
					return evaluate(self.Miss, context, event, *args, **kwargs)
				ret.update(result)

			elif isinstance(item, dict):
				if group is None:
					continue
				assert(len(item) == 1)

				key, value = next(iter(item.items()))

				if isinstance(value, Expression):
					v = evaluate(value, context, event, group, *args, **kwargs)
					if v is not None:
						ret[key] = v

				elif isinstance(value, list):
					for valuei in value:
						v = evaluate(valuei, context, event, group, *args, **kwargs)
						if v is not None:
							ret[key] = v
							break

				else:
					raise RuntimeError("Unexpected type: '{}'".format(value))
			else:
				ret[item] = group

		if self.Set is not None:
			for key, value in self.Set.items():
				v = evaluate(value, context, event, ret, *args, **kwargs)
				if v is not None:
					ret[key] = v

		if self.Update is not None:
			update_dict = evaluate(self.Update, context, event, ret, *args, **kwargs)
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

	def __init__(self, app, location, *, arg_regex, arg_replace, arg_what):
		super().__init__(app, location)
		self.Value = arg_what
		self.Regex = re.compile(arg_regex)
		self.Replace = arg_replace

	def __call__(self, context, event, *args, **kwargs):
		value = evaluate(self.Value, context, event, *args, **kwargs)
		repl = evaluate(self.Replace, context, event, *args, **kwargs)
		return self.Regex.sub(repl, value)


class REGEX_SPLIT(Expression):

	def __init__(self, app, location, *, arg_regex, arg_what, arg_max=0):
		super().__init__(app, location)
		self.Value = arg_what
		self.Regex = re.compile(arg_regex)
		self.Max = arg_max

	def __call__(self, context, event, *args, **kwargs):
		value = evaluate(self.Value, context, event, *args, **kwargs)
		maxsplit = evaluate(self.Max, context, event, *args, **kwargs)
		return self.Regex.split(value, maxsplit=maxsplit)


class REGEX_FINDALL(Expression):

	def __init__(self, app, location, *, arg_regex, arg_what):
		super().__init__(app, location)
		self.Value = arg_what
		self.Regex = re.compile(arg_regex)

	def __call__(self, context, event, *args, **kwargs):
		value = evaluate(self.Value, context, event, *args, **kwargs)
		return self.Regex.findall(value)
