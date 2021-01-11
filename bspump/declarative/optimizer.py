import logging

from .abc import Expression
from .expression.value.valueexpr import VALUE

###

L = logging.getLogger(__name__)

###


class ExpressionOptimizer(object):
	"""
	Optimizes an expression using walk strategy and individual optimize methods.
	"""

	def __init__(self, app):
		self.App = app


	def optimize(self, expression):

		# We run optimizations till we finish tree walk without any optimization found
		retry = True
		while retry:
			retry = False

			if not isinstance(expression, Expression):
				expression = VALUE(self.App, value=expression)

			# Walk the syntax tree
			for parent, key, obj in expression.walk():

				# Iterate through dict child items
				if isinstance(obj, dict):
					for _key, _value in obj.items():
						obj[_key] = self.optimize(_value)
					continue

				if not isinstance(obj, Expression):
					continue

				# Check if the node could be optimized
				opt_obj = obj.optimize()
				if opt_obj is None:
					continue

				if parent is None:
					expression = opt_obj
				else:
					# If yes, replace a given node by the optimized variant
					parent.set(key, opt_obj)

				# ... and start again
				retry = True
				break

		return expression


	def optimize_many(self, expressions):
		return [self.optimize(expression) for expression in expressions]
