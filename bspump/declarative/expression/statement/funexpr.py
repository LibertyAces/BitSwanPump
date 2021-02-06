from ...abc import Expression
from ..value.valueexpr import VALUE


class FUNCTION(Expression):

	Attributes = {
		"Apply": ["*"],
	}

	Category = 'Statements'


	def __init__(self, app, *, arg_apply, arg_name: str = None):
		super().__init__(app)

		if isinstance(arg_apply, Expression):
			self.Apply = arg_apply
		else:
			self.Apply = VALUE(app, value=arg_apply)

		if arg_name is not None:
			assert(isinstance(arg_name, str))
			self.Name = arg_name
		else:
			self.Name = None  # Anonymous function


	def __call__(self, context, event, *args, **kwargs):
		return self.Apply(context, event, *args, **kwargs)


	def get_outlet_type(self):
		return self.Apply.get_outlet_type()
