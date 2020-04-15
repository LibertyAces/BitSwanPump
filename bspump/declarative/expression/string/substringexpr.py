from ...abc import Expression


class SUBSTRING(Expression):

	def __init__(self, app, *, arg_value, arg_from, arg_to):
		super().__init__(app)
		self.Value = arg_value
		self.From = arg_from
		self.To = arg_to

	def __call__(self, context, event, *args, **kwargs):
		_string = self.evaluate(self.Value, context, event, *args, **kwargs)
		_from = self.evaluate(self.From, context, event, *args, **kwargs)
		_to = self.evaluate(self.To, context, event, *args, **kwargs)
		return _string[_from:_to]
