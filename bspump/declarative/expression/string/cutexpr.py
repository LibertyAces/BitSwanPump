import logging

from ...abc import Expression
from ...declerror import DeclarationError

###

L = logging.getLogger(__name__)

###


class CUT(Expression):

	Attributes = {
		"Value": ["str"],
		"Delimiter": ["str"],
		"Field": ["*"],  # TODO: This ...
	}

	Category = "String"


	def __init__(self, app, *, arg_what, arg_delimiter, arg_field):
		super().__init__(app)

		self.Value = arg_what

		# TODO: Delimiter must be a single character string
		self.Delimiter = arg_delimiter

		# Must be an integer
		self.Field = arg_field

	def get_outlet_type(self):
		return str.__name__

	def consult_inlet_type(self, key, child):
		return str.__name__

	def __call__(self, context, event, *args, **kwargs):

		try:
			value = self.Value(context, event, *args, **kwargs)
			x = value.split(self.Delimiter, self.Field + 1)
			return x[self.Field]

		except Exception as e:
			L.exception("The following exception ocurred in !CUT expression [delimiter: {}, field: {}]".format(
				self.Delimiter, self.Field
			))
			raise DeclarationError(original_exception=e, location=self.get_location())
