import bspump

from .builder import ExpressionBuilder


class DeclarativeProcessor(bspump.Processor):

	@classmethod
	def construct(cls, app, pipeline, definition: dict):
		_id = definition.get("id")
		config = definition.get("config")
		expression = definition.get("expression")
		return cls(app, pipeline, expression=expression, id=_id, config=config)

	def __init__(self, app, pipeline, declaration, id=None, config=None):
		super().__init__(app, pipeline, id=id, config=config)
		builder = ExpressionBuilder(app)
		self.Expression = builder.parse(declaration)

	def process(self, context, event):
		return self.Expression(context, event)
