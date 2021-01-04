import re
import urllib.parse

from ...abc import Expression, evaluate


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
		"Set": ["*"],  # TODO: This ...
		"Unset": ["*"],  # TODO: This ...
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

		if arg_set is not None:
			assert(isinstance(arg_set, dict))
		self.Set = arg_set

		if arg_unset is not None:
			assert(isinstance(arg_unset, list))
		self.Unset = arg_unset

		self.Update = arg_update


	def __call__(self, context, event, *args, **kwargs):
		value = evaluate(self.Value, context, event, *args, **kwargs)
		ret = self.Parser(context, value)

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
