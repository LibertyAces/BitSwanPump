from ..abc import Expression


class LOOKUP(Expression):

	def __init__(self, app, expression: dict):
		super().__init__(app, expression)
		svc = app.get_service("bspump.PumpService")
		self.Lookup = svc.locate_lookup(expression["lookup_id"])
		self.Key = expression["key"]

	def __call__(self, context, event, *args, **kwargs):
		return self.Lookup.get(self.Key)
