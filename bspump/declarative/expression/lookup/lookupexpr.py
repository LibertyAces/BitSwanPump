from ...abc import Expression, evaluate


class LOOKUP(Expression):

	def __init__(self, app, *, arg_in, arg_what):
		super().__init__(app)
		svc = app.get_service("bspump.PumpService")
		self.Lookup = svc.locate_lookup(arg_in)
		self.Key = arg_what


	def __call__(self, context, event, *args, **kwargs):
		# TODO: Not correct
		return self.Lookup.get(evaluate(self.Key, context, event, *args, **kwargs))
