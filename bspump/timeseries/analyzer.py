import logging

from ..analyzer.timewindowanalyzer import TimeWindowAnalyzer
from ..model.model import Model

###

L = logging.getLogger(__name__)

###


class TimeSeriesPredictor(TimeWindowAnalyzer):
	'''
	'''

	ConfigDefaults = {
		'path': '',
		'predicted_attribute': 'predicted'
	}

	def __init__(self, app, pipeline, model, matrix_id=None, dtype=[('value', 'f8'), ('predicted', 'f8'), ('count', 'i8')], 
					columns=15, analyze_on_clock=False, resolution=60, start_time=None, clock_driven=False, 
					id=None, config=None):

		super().__init__(app, pipeline, matrix_id=matrix_id, dtype=dtype, columns=columns, 
						analyze_on_clock=analyze_on_clock, resolution=resolution, start_time=start_time,
						clock_driven=clock_driven, id=id, config=config)

		self.Model = model
		self.PredictedAttribute = self.Config['predicted_attribute']
		self.initialize_window()


	def initialize_window(self):
		pass


	# Override it if needed
	def enrich(self, context, event, predicted):
		event[self.PredictedAttribute] = predicted


	def assign(self, *args):
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
		pass
