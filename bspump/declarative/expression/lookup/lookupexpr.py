from ..abc import Expression


class LOOKUP(Expression):
	"""
	Obtains value from "lookup_id" using "key":

		{
			"class": "LOOKUP",
			"lookup_id": "lookup_id",
			"key": "key"
		}
	"""

	def __init__(self, app, expression_class_registry, expression: dict):
		super().__init__(app, expression_class_registry, expression)
		svc = app.get_service("bspump.PumpService")
		self.Lookup = svc.locate_lookup(expression["lookup_id"])
		self.Key = expression["key"]

	def __call__(self, context, event, *args, **kwargs):
		return self.Lookup.get(self.Key)
