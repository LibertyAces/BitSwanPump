import operator

from ..abc import SequenceExpression, Expression
from ..declerror import DeclarationError
from .value.valueexpr import VALUE
from .datastructs.itemexpr import ITEM, ITEM_optimized_EVENT_VALUE

from .value.eventexpr import EVENT
from .utility.context import CONTEXT


class ComparisonExpression(SequenceExpression):


	def __call__(self, context, event, *args, **kwargs):
		it = iter(self.Items)

		i = next(it)
		try:
			a = i(context, event, *args, **kwargs)
		except Exception as e:
			raise DeclarationError(original_exception=e, location=i.get_location())

		for i in it:

			try:
				b = i(context, event, *args, **kwargs)
			except Exception as e:
				raise DeclarationError(original_exception=e, location=i.get_location())

			if not self.Operator(a, b):
				return False
			a = b

		return True


	def get_outlet_type(self):
		return bool.__name__


class LT(ComparisonExpression):
	'''
	Operator '<'
	'''
	Operator = operator.lt


class LE(ComparisonExpression):
	'''
	Operator '<='
	'''
	Operator = operator.le


class EQ(ComparisonExpression):
	'''
	Operator '=='
	'''
	Operator = operator.eq

	Attributes = {
		"Items": [
			'si64', 'si8', 'si16', 'si32', 'si64', 'si128', 'si256',
			'ui8', 'ui16', 'ui32', 'ui64', 'ui128', 'ui256',
			'str'
		]
	}


	def optimize(self):
		if len(self.Items) == 2 and isinstance(self.Items[1], VALUE):

			if isinstance(self.Items[0], ITEM_optimized_EVENT_VALUE):
				return EQ_optimized_EVENT_VALUE(self)

			# The nested objects may not be optimized yet when this parent optimization is called
			if isinstance(self.Items[0], ITEM):
				if isinstance(self.Items[0].With, EVENT) and isinstance(self.Items[0].Item, VALUE):
					return EQ_optimized_EVENT_VALUE(self)
				elif isinstance(self.Items[0].With, CONTEXT) and isinstance(self.Items[0].Item, VALUE) and "." in self.Items[0].Item.Value:
					# Skip nested context from optimization
					return None
				else:
					return EQ_optimized_simple(self)

		return None


	def get_items_inlet_type(self):
		# Find the first usable type in the items
		for item in self.Items:
			outlet_type = item.get_outlet_type()
			if outlet_type not in frozenset(['^']):
				return outlet_type
		raise NotImplementedError("Cannot decide on items inlet type '{}'".format(self))


	def consult_inlet_type(self, key, child):
		return self.get_items_inlet_type()


class EQ_optimized_simple(EQ):

	def __init__(self, orig):
		super().__init__(orig.App, sequence=orig.Items)
		self.A = self.Items[0]
		assert isinstance(self.A, Expression)

		assert isinstance(self.Items[1], VALUE)
		self.B = self.Items[1].Value
		assert isinstance(self.B, (bool, str, int, float))


	def __call__(self, context, event, *args, **kwargs):
		return self.A(context, event, *args, **kwargs) == self.B


	def optimize(self):
		return None


class EQ_optimized_EVENT_VALUE(EQ):

	# TODO: Attributes = [...]

	def __init__(self, orig):
		super().__init__(orig.App, sequence=orig.Items)
		self.Akey = self.Items[0].Item.Value
		self.Adefault = self.Items[0].Default.Value

		assert isinstance(self.Items[1], VALUE)
		self.B = self.Items[1].Value
		assert isinstance(self.B, (bool, str, int, float))


	def __call__(self, context, event, *args, **kwargs):
		return event.get(self.Akey, self.Adefault) == self.B


	def optimize(self):
		return None


class NE(ComparisonExpression):
	'''
	Operator '!='
	'''
	Operator = operator.ne


class GE(ComparisonExpression):
	"""
	Operator '>='
	"""
	Operator = operator.ge


class GT(ComparisonExpression):
	"""
	Operator '>'
	"""
	Operator = operator.gt


	def get_items_inlet_type(self):
		return evaluate_items_inlet_type(self.Items)


class IS(ComparisonExpression):
	"""
	Operator 'is'
	"""
	Operator = operator.is_


class ISNOT(ComparisonExpression):
	"""
	Operator 'is not'
	"""
	Operator = operator.is_not


	def get_items_inlet_type(self):
		# Find the first usable type in the items
		for item in self.Items:
			outlet_type = item.get_outlet_type()
			if outlet_type not in frozenset(['^']):
				return outlet_type
		raise NotImplementedError("Cannot decide on items inlet type '{}'".format(self))


	def consult_inlet_type(self, key, child):
		return self.get_items_inlet_type()



def evaluate_items_inlet_type(items):

	strings = False
	signed_integers = False
	unsigned_integers = False
	max_integer_size = 0

	for item in items:
		outlet_type = item.get_outlet_type()
		if outlet_type == ['^']:
			continue

		iti = integer_type_info.get(outlet_type)
		if iti is not None:
			if max_integer_size < iti:
				max_integer_size = iti
			if outlet_type[:1] == 'u':
				unsigned_integers = True
			else:
				signed_integers = True
			continue


		raise NotImplementedError("Unsupported type '{}' in comparison operator".format(outlet_type))


	if strings is False and unsigned_integers is False and signed_integers is True:
		# Just signed integers found
		return 'si{}'.format(max_integer_size)

	if strings is False and signed_integers is False and unsigned_integers is True:
		# Just unsigned integers found
		return 'ui{}'.format(max_integer_size)

	if strings is False and signed_integers is True and unsigned_integers is True:
		if max_integer_size == 1:
			# Booleans are handed differently (this is weird combo anyway)
			return 'ui1'
		# Mix of signed and unsigned integers found
		return 'si{}'.format(max_integer_size << 1)

	return "?"


integer_type_info = {
	'ui1': 1,
	'si8': 8,
	'si16': 16,
	'si32': 32,
	'si64': 64,
	'si128': 128,
	'si256': 256,
	'ui8': 8,
	'ui16': 16,
	'ui32': 32,
	'ui64': 64,
	'ui128': 128,
	'ui256': 256,
}
