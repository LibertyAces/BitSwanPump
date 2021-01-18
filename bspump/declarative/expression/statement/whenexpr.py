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
		self.Attributes = []

		self.Else = VALUE(self.App, value=None)


	def initialize(self):
		for n, i in enumerate(self.Items):

			# `test/then` branch
			if 'test' in i and 'then' in i:
				assert(len(i) == 2)

				vtest = i['test']
				if not isinstance(vtest, Expression):
					vtest = VALUE(self.App, value=vtest)

				attr_name = 'Test{}'.format(n)
				setattr(self, attr_name, vtest)
				self.Attributes.append(attr_name)

				vthen = i['then']
				if not isinstance(vthen, Expression):
					vthen = VALUE(self.App, value=vthen)

				attr_name = 'Then{}'.format(n)
				setattr(self, attr_name, vthen)
				self.Attributes.append(attr_name)

				self.ItemsNormalized.append((vtest, vthen))

			# `else` branch
			elif 'else' in i:
				assert(len(i) == 1)
				assert('Else' not in self.Attributes)

				v = i['else']
				if not isinstance(v, Expression):
					v = VALUE(self.App, value=v)

				attr_name = 'Else'
				setattr(self, attr_name, v)
				self.Attributes.append(attr_name)

			else:
				raise RuntimeError("Unexpected items in '!WHEN': {}".format(i.keys()))


	def __call__(self, context, event, *args, **kwargs):
		for test, then in self.ItemsNormalized:
			res = test(context, event, *args, **kwargs)
			if res:
				return then(context, event, *args, **kwargs)

		return self.Else(context, event, *args, **kwargs)
