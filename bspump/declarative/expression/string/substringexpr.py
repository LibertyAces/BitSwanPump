from ...abc import Expression, evaluate


class SUBSTRING(Expression):

	def __init__(self, app, location, *, arg_what, arg_from=0, arg_to=-1):
		super().__init__(app, location)
		self.Value = arg_what
		self.From = arg_from
		self.To = arg_to

	def __call__(self, context, event, *args, **kwargs):
		_string = evaluate(self.Value, context, event, *args, **kwargs)
		_from = evaluate(self.From, context, event, *args, **kwargs)
		_to = evaluate(self.To, context, event, *args, **kwargs)
		return _string[_from:_to]
