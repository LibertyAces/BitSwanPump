from ...abc import Expression

from ...typesystem import Outlet
from ...typesystem import types


class VALUE(Expression):
	"""
	Simply returns the value
	"""

	Category = "Value"


	def __init__(self, app, *, value, outlet_type=None):
		assert(not isinstance(value, Expression))

		if outlet_type is not None:
			# Explicit type
			outlet = Outlet(
				outlet_type=outlet_type,
				constant=True,
			)
		else:
			outlet = infere_outlet_from_python_value(value)

		super().__init__(app, outlet=outlet)

		self.Value = value
		assert(self.Outlet.is_constant)


	def __call__(self, context, event, *args, **kwargs):
		return self.Value


def infere_outlet_from_python_value(value):
	if isinstance(value, str):
		# TODO: Consider also list[ui8] type
		# It means that the outlet should not be RESOLVED but rather CONSTRAINED
		return Outlet(
			outlet_type=types.Type_str,
			constant=True,
		)

	raise NotImplementedError("Type inference from python value type '{}'".format(type(value)))
