from ...abc import Expression

from ..value.valueexpr import VALUE


class SELF(Expression):


	Attributes = {
		"Event": ["*"],  # Must of the the same type as the whole expression
	}


	def __init__(self, app, *, arg_event):
		super().__init__(app)

		if isinstance(arg_event, Expression):
			self.Event = arg_event
		else:
			self.Event = VALUE(app, value=arg_event)

		self.Self = None  # Will be filled later


	def initialize(self, self_expression):
		self.Self = self_expression


	def __call__(self, context, event, *args, **kwargs):
		new_event = self.Event(context, event, *args, **kwargs)
		return self.Self(context, new_event, *args, **kwargs)


	def get_outlet_type(self):
		return self.Self.get_outlet_type()
