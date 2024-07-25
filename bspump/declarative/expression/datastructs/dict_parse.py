import re
import urllib.parse

from ..value.valueexpr import VALUE
from ...abc import Expression


class RegexABCParser(object):

	def __init__(self, app, regex):
		self.Regex = re.compile(regex)

	def __call__(self, context, value):
		return dict(self.Regex.findall(value))


class KeyValueSpaceParser(RegexABCParser):

	def __init__(self, app):
		super().__init__(app, r"\b(\w+)=(.*?)(?=\s\w+=\s*|$)")


class KeyValueDoubleQuotesSpaceParser(RegexABCParser):

	def __init__(self, app):
		super().__init__(app, r'\b(\w+)="(.*?)(?="\s\w+=\s*|"$)')


class QueryStringParser(object):

	def __init__(self, app):
		pass

	def __call__(self, context, value):
		return dict(urllib.parse.parse_qsl(value))


class DICT_PARSE(Expression):

	Attributes = {
		"Value": ["*"],  # TODO: This ...
		"Type": ["*"],  # TODO: This ...
		"Unset": [],  # TODO: This ...
		"Update": ["*"],  # TODO: This ...
	}

	def __init__(self, app, *, arg_what, arg_type=None, arg_set=None, arg_unset=None, arg_update=None):
		super().__init__(app)

		self.Value = arg_what
		self.Type = arg_type
		self.Parser = {
			'kvs': KeyValueSpaceParser,
			'kvdqs': KeyValueDoubleQuotesSpaceParser,
			'qs': QueryStringParser,
		}.get(arg_type, 'kvs')(app)

		self.ArgSet = arg_set
		self.Set = None

		if arg_unset is not None:
			assert isinstance(arg_unset, list)
		self.Unset = arg_unset

		self.Update = arg_update

	def set(self, key, value):
		setattr(self, key, value)

		if "Set" in key:
			self.Set[key[3:]] = value

	def initialize(self):
		if self.ArgSet is None:
			self.Set = None
		else:
			assert isinstance(self.ArgSet, dict)
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
		ret = self.Parser(context, value)

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
