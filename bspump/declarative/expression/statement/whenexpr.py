from ...abc import Expression

from ..value.valueexpr import VALUE


class WHEN(Expression):
	"""
	Checks "if" condition passes - it is an `if` on steroids ;-)

	!WHEN
	- is:
		!EQ
		- !ITEM EVENT eggs
		- 2
	then: eggs

	- is:
		!LT
		- 9
		- !ITEM EVENT potatoes
		- 11
	then: potatoes

	- else:
		Nah

	"""

	Attributes = False  # Filled during initialize() since attributes are dynamic


	def __init__(self, app, *, sequence):
		super().__init__(app)
		self.Items = sequence
		self.ItemsNormalized = []
		self.Attributes = {}
		self.OutletType = None  # Will be determined in `initialize()`
		self.Else = VALUE(self.App, value=None)

	def set(self, key, value):
		setattr(self, key, value)

		if "Test" in key:
			item_normalized = self.ItemsNormalized[int(key[4:])]
			self.ItemsNormalized[int(key[4:])] = (value, item_normalized[1])

		if "Then" in key:
			item_normalized = self.ItemsNormalized[int(key[4:])]
			self.ItemsNormalized[int(key[4:])] = (item_normalized[0], value)

	def initialize(self):

		item_counter = 0
		for n, i in enumerate(self.Items):

			# `test/then` branch
			if 'test' in i and 'then' in i:
				assert(len(i) == 2)

				vtest = i['test']
				if not isinstance(vtest, Expression):
					vtest = VALUE(self.App, value=vtest)

				attr_name = 'Test{}'.format(item_counter)
				setattr(self, attr_name, vtest)
				self.Attributes[attr_name] = [bool.__name__]

				vthen = i['then']
				if not isinstance(vthen, Expression):
					vthen = VALUE(self.App, value=vthen)

				attr_name = 'Then{}'.format(item_counter)
				setattr(self, attr_name, vthen)
				if self.OutletType is None:
					self.OutletType = vthen.get_outlet_type()
				self.Attributes[attr_name] = self.OutletType

				self.ItemsNormalized.append((vtest, vthen))
				item_counter += 1

			# `else` branch
			elif 'else' in i:
				assert(len(i) == 1)
				# TODO: Fix double-initialization when doing INCLUDE
				# assert('Else' not in self.Attributes)

				v = i['else']
				if not isinstance(v, Expression):
					v = VALUE(self.App, value=v)

				attr_name = 'Else'
				setattr(self, attr_name, v)
				if self.OutletType is None:
					self.OutletType = v.get_outlet_type()

				self.Attributes[attr_name] = self.OutletType

			else:
				raise RuntimeError("Unexpected items in '!WHEN': {}".format(i.keys()))


	def __call__(self, context, event, *args, **kwargs):
		for test, then in self.ItemsNormalized:
			res = test(context, event, *args, **kwargs)
			if res:
				return then(context, event, *args, **kwargs)

		return self.Else(context, event, *args, **kwargs)


	def get_outlet_type(self):
		return self.OutletType
