import logging

from ..analyzer.timewindowanalyzer import TimeWindowAnalyzer


###

L = logging.getLogger(__name__)

###


class TimeSeriesPredictor(TimeWindowAnalyzer):
	'''
	Trained model based time window analyzer, which collects
	data into time series and predicts certain value.
	'''

	ConfigDefaults = {
		'path': '',
		'predicted_attribute': 'predicted'
	}

	def __init__(
		self, app, pipeline, model, matrix_id=None,
		dtype=[('value', 'f8'), ('predicted', 'f8'), ('count', 'i8')],
		columns=15, analyze_on_clock=False, resolution=60, start_time=None,
		clock_driven=False, id=None, config=None):

		super().__init__(
			app, pipeline, matrix_id=matrix_id, dtype=dtype,
			columns=columns, analyze_on_clock=analyze_on_clock,
			resolution=resolution, start_time=start_time,
			clock_driven=clock_driven, id=id, config=config
		)

		self.Model = model
		self.PredictedAttribute = self.Config['predicted_attribute']
		self.initialize_window()


	def initialize_window(self):
		'''
		Specific initialization if needed.
		'''
		pass


	def enrich(self, context, event, predicted):
		'''
		Enriches event with predicted value, override if needed.
		'''
		event[self.PredictedAttribute] = predicted


	def assign(self, *args):
		'''
		Record predicted values into time window matrix (or anywhere) if needed.
		'''
		pass


	def process(self, context, event):
		if self.predicate(context, event):
			sample, column = self.evaluate(context, event)
		else:
			return event

		if sample is not None:
			transformed_sample = self.Model.transform(sample)
			predicted = self.Model.predict(transformed_sample)
			self.enrich(context, event, predicted)
			self.assign(predicted, column)
		else:
			self.enrich(context, event, None)

		return event


	def alarm(self, *args):
		'''
		Compare real value and predicted and raise an alarm.
		'''
		pass
