import logging
import time
import bspump
import bspump.common
import bspump.trigger
import bspump.analyzer
import numpy as np
import datetime
import tensorflow as tf
import json

##


L = logging.getLogger(__name__)


##


class MyApplication(bspump.BSPumpApplication):
	def __init__(self):
		super().__init__()
		svc = self.get_service("bspump.PumpService")
		svc.add_pipeline(MyPipeline(self))


class MyPipeline(bspump.Pipeline):
	def __init__(self, app, pipeline_id=None):
		super().__init__(app, pipeline_id)

		model = MyLSTMModel() # TODO
		self.build(
			bspump.random.RandomSource(app, self, choice=['a', 'b', 'c'], config={ # TODO line source
				'number': 1000000
			}).on(bspump.trigger.OpportunisticTrigger(app, chilldown_period=1)),
			TimestampEnricher(app, self),
			#MyTimeSeriesPredictor(app, self, model), # TODO
			bspump.common.PPrintSink(app, self)
		)


class TimeStampEnricher(bspump.Processor):
	def process(self, context, event):
		time_string = event['Timestamp']
		timestamp = datetime.datetime.strptime(time_string, '%Y-%m-%d %H:%M')
		event['@timestamp'] = timestamp
		return event


class MyTimeSeriesPredictor(bspump.timeseries.TimeSeriesPredictor):
	def __init__(self, app, pipeline, id=None, config=None): #TODO
		super().__init__(app, pipeline, id=id, config=config)# TODO

	# TODO upstream
	def process(self, context, event):
		if self.predicate(context, event):
			sample, column = self.evaluate(context, event)
		else:
			return event

		if sample is not None:
			transformed_sample = self.Model.transform(sample)
			predicted = self.Model.predict(transformed_sample)
			self.enrich(predicted, context, event)
			self.TimeWindow.Array[0, column, 2] = predicted
		else:
			self.preenrich(context, event)

		return event

	# TODO upstream
	def preenrich(self, context, event):
		event['predicted'] = None

	# TODO: upstream
	def enrich(self, predicted, context, event):
		event['predicted'] = predicted


	def initialize_window(self):
		self.TimeWindow.add_row('One and only row')

	def get_sample(self, column):
		if (column - self.Model.WindowSize) < 0:
			return None
		
		sample = self.TimeWindow.Array[0, (column - self.Model.WindowSize):column, 1]
		if np.any(sample == 0): # not ready
			return None

		return sample


	def evaluate(self, context, event):
		timestamp = event['@timestamp']
		column = self.TimeWindow.get_column(timestamp)
		if column is None:
			return None, None
		
		value = event['Count']
		self.TimeWindow.Array[0, column, 0] = value
		self.TimeWindow.Array[0, column, 1] += 1

		sample = self.get_sample(column)
		return sample, column


	def alarm(self):
		# TODO mask
		error = tf.keras.metrics.mean_absolute_error(self.TimeWindow.Array[0, :, 0], self.TimeWindow.Array[0, :, 2]).numpy()
		print(error)
		

	def analyze(self):
		# TODO export predicted
		pass



class MyLSTSMModel(bspump.model.Model):
	
	ConfigDefaults = {
		'path_model': '',
		'path_parameters': '',
	}

	def __init__(self, app, pipeline, id=None, config=None): #TODO
		super().__init__(app, pipeline, analyze_on_clock=True, dtype="({},)i2".format(self.HLLAggregator.m), id=id, config=config) #TODO
		self.PathModel = self.Config['path_model']
		self.PathParameters = self.Config['path_parameters']
		self.Model = self.load_model_from_file()
		self.Parameters = self.load_parameters_from_file()

	# TODO: upstream
	def load_parameters_from_file(self):
		with open(self.PathParameters) as f:
			self.Parameters = json.load(f)

	# TODO upstream
	def load_model_from_file(self):
		self.Model = tf.keras.models.load_model(self.Path)

	# TODODODODO
	def transform(self, sample):
		extended_sample = sample[..., np.newaxis]
		ds = tf.data.Dataset.from_tensor_slices(extended_sample)
		# ds = ds.window(self.PathParameters['window_size'], shift=1, drop_remainder=True) #TODO param
		# ds = ds.flat_map(lambda w: w.batch(self.PathParameters['window_size']))
		# ds = ds.batch(32).prefetch(1) # TODO?
		return ds


	def predict(self, data):
		forecast = self.Model.predict(data)
		return forecast[-1, -1, 0] # TODO wat?
	

if __name__ == '__main__':
	app = MyApplication()
	app.run()
