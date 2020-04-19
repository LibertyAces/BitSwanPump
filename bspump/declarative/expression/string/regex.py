import re

from ...abc import Expression


class REGEX(Expression):
	"""
	Checks if `value` matches with the `regex`, returns `hit` / `miss` respectively.
	"""

	def __init__(self, app, *, arg_regex, arg_value, arg_hit=True, arg_miss=False):
		super().__init__(app)
		self.Value = arg_value
		self.Regex = re.compile(arg_regex)
		self.Hit = arg_hit
		self.Miss = arg_miss
		# TODO: Regex flags

	def __call__(self, context, event, *args, **kwargs):
		value = self.evaluate(self.Value, context, event, *args, **kwargs)
		match = re.search(self.Regex, value)
		if match is None:
			return self.evaluate(self.Miss, context, event, *args, **kwargs)
		else:
			return self.evaluate(self.Hit, context, event, *args, **kwargs)


class REGEX_PARSE(Expression):
	"""
	Search `value` forr `regex` with regular expressions groups.
	If nothing is found `miss` is returned.
	Otherwise, groups are returned in as a list.

	If `fields` are provided, the groups are mapped to provided fields.
	"""

	def __init__(self, app, *, arg_regex, arg_items, arg_value, arg_miss=None):
		super().__init__(app)
		self.Value = arg_value
		self.Regex = re.compile(arg_regex)
		self.Miss = arg_miss
		self.Items = arg_items
		# TODO: Regex flags

	def __call__(self, context, event, *args, **kwargs):
		value = self.evaluate(self.Value, context, event, *args, **kwargs)
		try:
			match = re.search(self.Regex, value)
		except TypeError:
			match = None
		if match is None:
			return self.evaluate(self.Miss, context, event, *args, **kwargs)

		groups = match.groups()
		if self.Items is None:
			return groups

		ret = dict()
		for item, group in zip(self.Items, groups):
			if isinstance(item, Expression):
				result = item.evaluate(item, context, event, group, *args, **kwargs)
				if result is None:
					return self.evaluate(self.Miss, context, event, *args, **kwargs)
				ret.update(result)
			else:
				ret[item] = group

		return ret


class REGEX_REPLACE(Expression):
	"""
	Search `regex_search` in `value` and replace with `regex_replace`.
	"""

	def __init__(self, app, *, arg_regex_search, arg_regex_replace, arg_value):
		super().__init__(app)
		self.Value = arg_value
		self.RegexSearch = re.compile(arg_regex_search)
		self.RegexReplace = re.compile(arg_regex_replace)

	def __call__(self, context, event, *args, **kwargs):
		value = self.evaluate(self.Value, context, event, *args, **kwargs)
		return re.sub(self.RegexSearch, self.RegexReplace, value)
