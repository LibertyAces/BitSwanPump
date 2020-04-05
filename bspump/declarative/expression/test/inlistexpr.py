from ...abc import Expression


# TODO: This ...
class INLIST(Expression):
	"""
	Checks if expression is of given list:

		{
			"function": "INLIST",
			"list": [],
			"value": <EXPRESSION>
		}
	"""

	def __init__(self, app, *, arg_list, arg_value):
		super().__init__(app)
		self.List =arg_list
		self.Value = arg_value

	def __call__(self, context, event, *args, **kwargs):
		return self.Value(context, event, *args, **kwargs) in self.List
