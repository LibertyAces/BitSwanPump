from ...abc import Expression
from ..value.valueexpr import VALUE


class FUNCTION(Expression):

	Attributes = {
		"Do": ["*"],
	}


	def __init__(self, app, *, arg_do, arg_name: str = None):
		super().__init__(app)

		if isinstance(arg_do, Expression):
			self.Do = arg_do
		else:
			self.Do = VALUE(app, value=arg_do)

		if arg_name is not None:
			assert(isinstance(arg_name, str))
			self.Name = arg_name
		else:
			self.Name = None  # Anonymous function


	def __call__(self, context, event, *args, **kwargs):
		return self.Do(context, event, *args, **kwargs)


	def get_outlet_type(self):
		return self.Do.get_outlet_type()
