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

	def __init__(self, app, pipeline, declaration, library=None, id=None, config=None):
		super().__init__(app, pipeline, id=id, config=config)
		self.Declaration = declaration
		self.Builder = ExpressionBuilder(app, library)
		self.ExpressionOptimizer = ExpressionOptimizer(app)
		self.Expressions = None

	async def initialize(self):
		expressions = await self.Builder.parse(self.Declaration)
		self.Expressions = self.ExpressionOptimizer.optimize_many(expressions)

	def process(self, context, event):
		for expression in self.Expressions:
			event = expression(context, event)
			if event is None:
				return None

		if not event:
			return None

		return event
