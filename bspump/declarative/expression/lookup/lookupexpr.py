from ...abc import Expression


class LOOKUP_GET(Expression):

	Attributes = {
		"Key": ["*"],  # TODO: This ...
		"LookupID": ["*"],  # TODO: This ...
	}

	def __init__(self, app, *, arg_in, arg_what):
		super().__init__(app)
		self.PumpService = app.get_service("bspump.PumpService")
		self.LookupID = arg_in
		self.Key = arg_what


	def build_key(self, context, event, *args, **kwargs):
		if isinstance(self.Key, (list, tuple)):
			# Compound key
			result = list()
			for k in self.Key:
				if isinstance(k, (str, int, float)):
					result.append(k)
				else:
					result.append(k(context, event, **kwargs))
			return tuple(result)
		else:
			# Simple key
			if isinstance(self.Key, (str, int, float)):
				return self.Key
			else:
				return self.Key(context, event, **kwargs)


	def __call__(self, context, event, *args, **kwargs):
		lookup = self.PumpService.locate_lookup(self.LookupID, context)
		key = self.build_key(context, event, *args, **kwargs)
		return lookup.get(key)


class LOOKUP_CONTAINS(LOOKUP_GET):

	Attributes = {
		"Key": ["*"],  # TODO: This ...
		"LookupID": ["*"],  # TODO: This ...
	}

	def __call__(self, context, event, *args, **kwargs):
		lookup = self.PumpService.locate_lookup(self.LookupID, context)
		key = self.build_key(context, event, *args, **kwargs)
		return lookup.get(key) is not None
