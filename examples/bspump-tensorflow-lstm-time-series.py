import logging
import time

import bspump
import bspump.common
import bspump.file
import bspump.trigger
import bspump.analyzer
import bspump.model
import bspump.timeseries

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

		model = MyLSTMModel(self, id='MyModel', config={'path_model': 'examples/timeseries/my_model.h5', 
												'path_parameters': 'examples/timeseries/my_parameters.json'})
		self.build(
			bspump.file.FileCSVSource(app, self, config={
				'path':'examples/timeseries/data.csv'
			}).on(bspump.trigger.OpportunisticTrigger(app)),
			TimestampEnricher(app, self),
			MyTimeSeriesPredictor(app, self, model),
			bspump.common.PPrintSink(app, self)
		)


class TimestampEnricher(bspump.Processor):
	def process(self, context, event):
		time_string = event['Timestamp']
		timestamp = datetime.datetime.strptime(time_string, '%Y-%m-%d %H:%M')
		event['@timestamp'] = int(timestamp.timestamp())
		return event


class MyTimeSeriesPredictor(bspump.timeseries.TimeSeriesPredictor):
	def __init__(self, app, pipeline, model, start_time=1584108000, resolution=3600, columns=493, id=None, config=None):
		super().__init__(app, pipeline, model, start_time=start_time, resolution=resolution, columns=columns, id=id, config=config)
		pipeline.PubSub.subscribe("bspump.file_source.no_files!", self.analyze)
		self.App = app

	def initialize_window(self):
		self.TimeWindow.add_row('One and only row')

	def get_sample(self, column):
		if (column - self.Model.WindowSize) < 0:
			return None
		
		sample = self.TimeWindow.Array[0, (column - self.Model.WindowSize):column]
		# if np.any(sample['count'] == 0): # not ready
		# 	return None

		return sample['value']


	def evaluate(self, context, event):
		timestamp = event['@timestamp']
		column = self.TimeWindow.get_column(timestamp)
		if column is None:
			return None, None
		
		value = int(event['Count'])
		self.TimeWindow.Array[0, column]['value'] = value
		self.TimeWindow.Array[0, column]['count'] += 1

		sample = self.get_sample(column)
		return sample, column


	def assign(self, value, column):
		self.TimeWindow.Array[0, column]['predicted'] = value
	

	def alarm(self):
		error = tf.keras.metrics.mean_absolute_error(self.TimeWindow.Array[0, :]['value'], self.TimeWindow.Array[0, :]['predicted']).numpy()
		print('mean absolute error', error)
		

	async def analyze(self, message_type):
		print("Analyzing...")
		self.alarm()
		predicted = self.TimeWindow.Array[0, :]['predicted'].tolist()
		with open("examples/timeseries/exported.json", "w") as f:
			json.dump({'predicted': predicted}, f)
		
		print("Done!")
		self.App.stop()


class MyLSTMModel(bspump.model.Model):

	def __init__(self, app, id=None, config=None):
		super().__init__(app, id=id, config=config)
		self.load_model_from_file()
		self.load_parameters_from_file()
		self.WindowSize = self.Parameters['window_size']


	def load_model_from_file(self):
		self.TrainedModel = tf.keras.models.load_model(self.PathModel)


	def transform(self, sample):
		extended_sample = sample[..., np.newaxis]
		ds = tf.data.Dataset.from_tensor_slices(extended_sample)
		ds = ds.window(self.WindowSize, shift=1, drop_remainder=True)
		ds = ds.flat_map(lambda w: w.batch(self.WindowSize))
		ds = ds.batch(1).prefetch(1)
		return ds


	def predict(self, data):
		forecast = self.TrainedModel.predict(data)
		return forecast[-1, -1, 0]
	

if __name__ == '__main__':
	app = MyApplication()
	app.PubSub.publish("go!")
	app.run()

