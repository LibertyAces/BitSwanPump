from ..analyzer import TimeWindowAnalyzer
from .builder import ExpressionBuilder


class DeclarativeTimeWindowAnalyzer(TimeWindowAnalyzer):


	@classmethod
	def construct(cls, app, pipeline, definition: dict):
		_id = definition.get("id")
		config = definition.get("config")
		declaration = definition.get("declaration")
		return cls(app, pipeline, declaration=declaration, id=_id, config=config)


	def __init__(self, app, pipeline, declaration, id=None, config=None):

		builder = ExpressionBuilder(app)
		decl = builder.parse(declaration)
		config = decl.pop('config')
		self.Predicate = decl.pop('predicate')

		dtype = config.get('dtype', 'float_')

		columns = config.get('columns', {}).get('count', 15)
		resolution = config.get('columns', {}).get('resolution', 15)

		self.Targets = decl

		super().__init__(app, pipeline, id=id, config=config,
			dtype=dtype,  columns=columns, resolution=resolution,
			# TODO: matrix_id
			# TODO: analyze_on_clock
			# TODO: start_time
			# TODO: clock_driven
		)



	def process(self, context, event):
		x = self.Predicate(context, event)
		if x:
			if x == True: x = 'evaluate'
			if isinstance(x, list):
				for i in x:
					evaluate = self.Targets[i]
					evaluate(context, event)

			else:
				evaluate = self.Targets[x]
				evaluate(context, event)

		return event

