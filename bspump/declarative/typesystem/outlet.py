from .info import name_to_type
from .types import TypeABC


class Outlet(object):


	def __init__(self, *, outlet_type=None, constant=None, constrains=None):
		self.Constant = constant  # or True / False

		if outlet_type is not None:
			if isinstance(outlet_type, str):
				outlet_type = name_to_type[outlet_type]
			assert(issubclass(outlet_type, TypeABC))
			self.Type = outlet_type
		else:
			self.Type = None

		if constrains is None:
			self.Constrains = None
		else:
			self.Constrains = constrains[:]  # Make a copy


	def get_status(self):
		if self.Type is not None:
			return "RESOLVED"
		elif self.Constrains is not None:
			return "CONSTRAINED"
		else:
			return "UNCONSTRAINED"


	def is_constant(self):
		'''
		Returns:
		- `True`: The outlet is constant, it means it will not change during run-time
		- `False`: The outlet is variable
		- `None`: Undecided yet
		'''
		return self.Constant


def get_type_constrains_from_value(value):
	value_type = type(value)
	if value_type is str:
		return [
			("String"),
			("List"),
		]

	raise NotImplementedError("Infering type constrains not implemented for '{}'".format(value_type))
