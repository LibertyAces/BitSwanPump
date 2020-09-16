from bspump.declarative.abc import Expression, evaluate

from ..value.eventexpr import ARG

import logging

#

L = logging.getLogger(__name__)

#


class CAST(Expression):
	"""
	Casts "value" to "type"
	"""

	def __init__(self, app, *, arg_what=None, arg_type=None, arg_default=None, value=None):
		super().__init__(app)

		if value is not None:
			# Scalar variant

			self.Value = ARG(app=app, value='')

			# Detect type cast function
			if value == "int":
				self.Conversion = int
			elif value == "float":
				self.Conversion = float
			elif value == "str":
				self.Conversion = str
			elif value == "dict":
				self.Conversion = dict
			elif value == "list":
				self.Conversion = list
			else:
				raise RuntimeError("Unsupported type '{}' found in CAST expression.".format(arg_type))


		else:
			self.Value = arg_what

			# Detect type cast function
			if arg_type == "int":
				self.Conversion = int
			elif arg_type == "float":
				self.Conversion = float
			elif arg_type == "str":
				self.Conversion = str
			elif arg_type == "dict":
				self.Conversion = dict
			elif arg_type == "list":
				self.Conversion = list
			else:
				raise RuntimeError("Unsupported type '{}' found in CAST expression.".format(arg_type))

		self.Default = arg_default


	def __call__(self, context, event, *args, **kwargs):
		try:
			return self.Conversion(evaluate(self.Value, context, event, *args, **kwargs))
		except (ValueError, AttributeError, TypeError) as e:
			# TODO: Remove eventually when there are more occurrences among other expressions as well
			L.warning("When performing cast, the following error occurred: '{}'. Using default value.".format(e))
			if self.Default is None:
				return None
			return evaluate(self.Default, context, event, *args, **kwargs)
