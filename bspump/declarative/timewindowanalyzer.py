from ..analyzer import TimeWindowAnalyzer
from .builder import ExpressionBuilder
from .abc import Expression, evaluate


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
		define = decl.pop('define')
		self.Predicate = decl.pop('predicate')

		matrixes = define.pop('matrixes', {})
		dtype = matrixes.pop('primary', {}).get('cell', {})
		if isinstance(dtype, dict):
			dtype = {
				"names": list(dtype.keys()),
				"formats": list(dtype.values()),
			}

		columns = define.pop('columns', {})
		columns_count = columns.pop('count', 15)
		columns_resolution = columns.pop('resolution', 15)
		self.ColumnItem = columns.pop('item', 'timestamp')

		self.Evaluates = decl.pop('evaluate')
		assert isinstance(self.Evaluates, dict)

		self.Dimension = define.pop('dimension')
		assert isinstance(self.Dimension, list) or isinstance(self.Dimension, str)

		self.Trigger = decl.pop('trigger', None)
		if self.Trigger is not None:
			assert isinstance(self.Trigger, list)

		# TODO: matrix_id
		# TODO: analyze_on_clock
		# TODO: start_time
		# TODO: clock_driven
		super().__init__(
			app, pipeline, id=id, config=config,
			dtype=dtype, columns=columns_count, resolution=columns_resolution,
		)

	def process(self, context, event):
		x = self.Predicate(context, event)
		if x:
			if x:
				x = 'evaluate'
			if isinstance(x, list):
				for i in x:
					evaluate(self.Evaluates[i], context, event)
			else:
				evaluate(self.Evaluates[x], context, event)

		return event

	def evaluate(self, evalobj, context, event):

		# Find the column in timewindow matrix to fit in
		column = event[self.ColumnItem]
		column = self.TimeWindow.get_column(column)
		if column is None:
			return

		# Find the row, existing or create a new one
		row_key = tuple(event[item] for item in self.Dimension)
		row = self.TimeWindow.get_row_index(row_key)
		if row is None:
			row = self.TimeWindow.add_row(row_key)

		cell = self.TimeWindow.Array[row, column]

		matrix = evalobj.get('primary')
		if isinstance(matrix, Expression):
			ret = evaluate(
				matrix, context, event,
				cell,
				row=row,
				column=column,
			)
		else:
			ret = matrix

		self.TimeWindow.Array[row, column] = ret
		self.trigger(context, event, 'primary', ret, row, column)

	def trigger(self, context, event, matrix, cell, row, column):
		for t in self.Trigger:
			matrix = t[matrix]
			test = matrix['test']
			result = evaluate(
				test, context, event,
				cell,
				row=row,
				column=column,
			)

			if result:
				print(">>> trigger", event, row, column)
