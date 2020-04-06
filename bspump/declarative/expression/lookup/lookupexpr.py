from ...abc import Expression


class LOOKUP(Expression):
	"""
	Obtains value from "lookup" (id of the lookup) using "key".
	"""

	def __init__(self, app, *, arg_lookup, arg_key):
		super().__init__(app)
		svc = app.get_service("bspump.PumpService")
		self.Lookup = svc.locate_lookup(arg_lookup)
		self.Key = arg_key

	def __call__(self, context, event, *args, **kwargs):
		# TODO: Not correct
		return self.Lookup.get(self.evaluate(self.Key, context, event, *args, **kwargs))
