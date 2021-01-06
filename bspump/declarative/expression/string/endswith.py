from ...abc import Expression, evaluate
from ..value.valueexpr import VALUE


class ENDSWITH(Expression):

	Attributes = {
		"What": ["*"],  # TODO: This ...
		"Postfix": ["*"],  # TODO: This ...
	}

	def __init__(self, app, *, arg_what, arg_postfix):
		super().__init__(app)
		self.What = arg_what

		if not isinstance(arg_postfix, Expression):
			self.Postfix = VALUE(app, value=arg_postfix)
		else:
			self.Postfix = arg_postfix

	def __call__(self, context, event, *args, **kwargs):
		value = evaluate(self.What, context, event, *args, **kwargs)
		if value is None:
			return False

		postfix = evaluate(self.Postfix, context, event, *args, **kwargs)
		return value.endswith(postfix)
