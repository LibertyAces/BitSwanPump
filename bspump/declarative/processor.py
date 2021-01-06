from ..abc.processor import Processor
from .builder import ExpressionBuilder
from .optimizer import ExpressionOptimizer


class DeclarativeProcessor(Processor):

	@classmethod
	def construct(cls, app, pipeline, definition: dict):
		_id = definition.get("id")
		config = definition.get("config")
		declaration = definition.get("declaration")
		return cls(app, pipeline, declaration=declaration, id=_id, config=config)

	def __init__(self, app, pipeline, declaration, libraries=None, id=None, config=None):
		super().__init__(app, pipeline, id=id, config=config)
		builder = ExpressionBuilder(app, libraries)
		optimizer = ExpressionOptimizer(app)
		expressions = builder.parse(declaration)
		self.Expressions = optimizer.optimize_many(expressions)

	def process(self, context, event):
		for expression in self.Expressions:
			event = expression(context, event)
			if event is None:
				return None
		return event
