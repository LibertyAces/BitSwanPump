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
			return self.evaluate(self.Miss, event, *args, **kwargs)
		else:
			return self.evaluate(self.Hit, event, *args, **kwargs)


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
		match = re.search(self.Regex, value)
		if match is None:
			return self.evaluate(self.Miss, event, *args, **kwargs)

		groups = match.groups()
		if self.Items is None:
			return groups

		return dict(zip(self.Items, groups))
