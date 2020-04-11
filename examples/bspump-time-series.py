import logging
import time
import bspump
import bspump.common
import bspump.trigger
import bspump.analyzer
import numpy as np
import datetime

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
	def __init__(self, app, pipeline, id=None, config=None):
		super().__init__(app, pipeline, id=id, config=config)
		self.Values = set()
	
	

	def evaluate(self, context, event):
		pass

	def enrich(self, context, event):
		pass

	def alarm(self, context, event):
		pass
		

	def analyze(self):
		# TODO export
		pass



class MyLSTSMModel(bspump.model.Model):

	def __init__(self, app, pipeline, id=None, config=None): #TODO
		# add path
		super().__init__(app, pipeline, analyze_on_clock=True, dtype="({},)i2".format(self.HLLAggregator.m), id=id, config=config) #TODO
		# TODO load_from_file
		self.Model = None

	def load_from_file(self):
		# TODO upstream
		pass

	# TODODODODO
	def transform(self, context, sample):
		extended_sample = sample[..., np.newaxis]
		ds = tf.data.Dataset.from_tensor_slices(extended_sample)
		ds = ds.window(window_size, shift=1, drop_remainder=True) #TODO param
		ds = ds.flat_map(lambda w: w.batch(window_size))
		ds = ds.batch(32).prefetch(1) # TODO?
		return ds


	def predict(self, data):
		forecast = self.Model.predict(data)
		return forecast[:, -1, 0] # TODO wat?
	

if __name__ == '__main__':
	app = MyApplication()
	app.run()
