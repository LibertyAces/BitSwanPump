from bspump.declarative.abc import Expression

from ..value.eventexpr import ARG
from ..value.valueexpr import VALUE

import logging

#

L = logging.getLogger(__name__)

#


class CAST(Expression):
	"""
	Casts "value" to "type"
	"""

	Attributes = {
		"What": ["*"],
		"Default": ["*"],
	}

	CastMap = {
		'bool': (bool, bool.__name__),
		'ui1': (bool, bool.__name__),
		'si1': (bool, bool.__name__),

		'int': (int, int.__name__),
		'si8': (int, 'si8'),
		'si16': (int, 'si16'),
		'si32': (int, 'si32'),
		'si64': (int, 'si64'),
		'si128': (int, 'si128'),
		'si256': (int, 'si256'),

		'ui8': (int, 'ui8'),
		'ui16': (int, 'ui16'),
		'ui32': (int, 'ui32'),
		'ui64': (int, 'ui64'),
		'ui128': (int, 'ui128'),
		'ui256': (int, 'ui256'),

		'float': (float, float.__name__),
		'fp16': (float, float.__name__),
		'fp32': (float, float.__name__),
		'fp64': (float, float.__name__),
		'fp128': (float, float.__name__),

		'str': (str, str.__name__),
		'dict': (dict, dict.__name__),
		'list': (list, list.__name__),

	}


	def __init__(self, app, *, arg_what=None, arg_type=None, arg_default=None, value=None):
		super().__init__(app)

		if value is not None:
			# Scalar variant
			# TODO (Dec 2020, AT): This one (scalar variant) is weird, not sure if used anywhere

			self.What = ARG(app=app, value='')
			self.Conversion, self.OutletType = self.CastMap[value]

		else:
			if isinstance(arg_what, Expression):
				self.What = arg_what
			else:
				self.What = VALUE(app, value=arg_what)

			# Detect type cast function
			self.Conversion, self.OutletType = self.CastMap[arg_type]


		if isinstance(arg_default, Expression):
			self.Default = arg_default
		else:
			self.Default = VALUE(app, value=arg_default)


	def __call__(self, context, event, *args, **kwargs):
		try:
			return self.Conversion(self.What(context, event, *args, **kwargs))
		except (ValueError, AttributeError, TypeError):
			if self.Default is None:
				return None
			return self.Default(context, event, *args, **kwargs)


	def get_outlet_type(self):
		return self.OutletType
