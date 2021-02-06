from ...abc import Expression
from ..value.valueexpr import VALUE


class ENDSWITH(Expression):

	Attributes = {
		"What": ["str"],
		"Postfix": ["str"],
	}

	Category = "String"


	def __init__(self, app, *, arg_what, arg_postfix):
		super().__init__(app)
		self.What = arg_what

		if not isinstance(arg_postfix, Expression):
			self.Postfix = VALUE(app, value=arg_postfix)
		else:
			self.Postfix = arg_postfix

	def get_outlet_type(self):
		return bool.__name__

	def consult_inlet_type(self, key, child):
		return str.__name__

	def __call__(self, context, event, *args, **kwargs):
		value = self.What(context, event, *args, **kwargs)
		if value is None:
			return False

		postfix = self.Postfix(context, event, *args, **kwargs)
		return value.endswith(postfix)
