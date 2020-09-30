from ..abc.processor import Processor
from .builder import ExpressionBuilder


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
		self.Expression = builder.parse(declaration)

	def process(self, context, event):
		return self.Expression(context, event)
