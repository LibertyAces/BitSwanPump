from ...abc import Expression, evaluate


class LOOKUP_GET(Expression):

	def __init__(self, app, *, arg_in, arg_what):
		super().__init__(app)
		self.PumpService = app.get_service("bspump.PumpService")
		self.LookupID = arg_in
		self.Key = arg_what


	def build_key(self, context, event, *args, **kwargs):
		if isinstance(self.Key, (list, tuple)):
			# Compound key
			return tuple(
				evaluate(k, context, event, *args, **kwargs) for k in self.Key
			)
		else:
			# Simple key
			return evaluate(self.Key, context, event, *args, **kwargs)


	def __call__(self, context, event, *args, **kwargs):
		lookup = self.PumpService.locate_lookup(self.LookupID, context)
		key = self.build_key(context, event, *args, **kwargs)
		return lookup.get(key)


class LOOKUP_CONTAINS(LOOKUP_GET):

	def __call__(self, context, event, *args, **kwargs):
		lookup = self.PumpService.locate_lookup(self.LookupID, context)
		key = self.build_key(context, event, *args, **kwargs)
		return lookup.get(key) is not None
