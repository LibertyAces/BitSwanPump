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
		counter = 0
		while retry:
			retry = False

			counter += 1

			if not isinstance(expression, Expression):
				expression = VALUE(self.App, value=expression)

			# Walk the syntax tree
			for parent, key, obj in expression.walk():

				if not isinstance(obj, Expression):
					continue

				# Check if the node could be optimized
				opt_obj = obj.optimize()
				if opt_obj is None:
					continue

				assert obj is not opt_obj

				if parent is None:
					expression = opt_obj
				else:
					# If yes, replace a given node by the optimized variant
					parent.set(key, opt_obj)

				if counter > 100000:
					raise RuntimeError("Optimization likely stucked at '{}'-'{}'-'{}'/'{}'".format(parent, key, obj, opt_obj))

				# ... and start again
				retry = True
				break

		return expression


	def optimize_many(self, expressions):
		return [self.optimize(expression) for expression in expressions]
