from ...abc import Expression, evaluate
from ..value.valueexpr import VALUE


class SUBSTRING(Expression):

	Attributes = {
		"Value": ["*"],  # TODO: This ...
		"From": ["*"],  # TODO: This ...
		"To": ["*"],  # TODO: This ...
	}

	def __init__(self, app, *, arg_what, arg_from=0, arg_to=-1):
		super().__init__(app)
		self.Value = arg_what

		if not isinstance(arg_from, Expression):
			self.From = VALUE(app, value=arg_from)
		else:
			self.From = arg_from

		if not isinstance(arg_to, Expression):
			self.To = VALUE(app, value=arg_to)
		else:
			self.To = arg_to

	def __call__(self, context, event, *args, **kwargs):
		_string = evaluate(self.Value, context, event, *args, **kwargs)
		_from = evaluate(self.From, context, event, *args, **kwargs)
		_to = evaluate(self.To, context, event, *args, **kwargs)
		return _string[_from:_to]
