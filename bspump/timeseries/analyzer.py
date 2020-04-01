import logging

from .analyzer import TimeWindowAnalyzer
from .model import Model

###

L = logging.getLogger(__name__)

###


class TimeSeriesModelAnalyzer(TimeWindowAnalyzer):
	'''
	'''

	ConfigDefaults = {
		'path': '',
	}

	def __init__(self, app, pipeline, model, matrix_id=None, dtype='float_', columns=15, 
					analyze_on_clock=False, resolution=60, start_time=None, clock_driven=True, 
					id=None, config=None):

		super().__init__(app, pipeline, matrix_id=matrix_id, dtype='dtype', columns=columns, 
				analyze_on_clock=analyze_on_clock, resolution=resolution, start_time=start_time,
				clock_driven=clock_driven, id=id, config=config)

		self.Model = model
		# TODO add params

	def process(self, context, event):
		if self.predicate(context, event):
			data = self.evaluate(context, event) 
			# NOTE!

		if data is not None:
			transformed_data = self.Model.transform(data)
			predicted = self.Model.predict(transformed_data)
			self.enrich(predicted, context, event)

		return event


	def enrich(self, predicted, context, event):
		pass


	def alarm(self, *args):
		pass
