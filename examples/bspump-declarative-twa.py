import logging
import datetime

import bspump
import bspump.common
import bspump.declarative
import bspump.file
import bspump.trigger

##

L = logging.getLogger(__name__)

##

class Covid19Pipeline(bspump.Pipeline):

	def __init__(self, app, pipeline_id=None):
		super().__init__(app, pipeline_id)

		self.build(

			bspump.file.FileCSVSource(app, self, config={'path':'./data/covid19-cases-head.csv','post':'noop'}
			).on(bspump.trigger.PubSubTrigger(app, "go!", pubsub=self.PubSub)),
			Covid19Enricher(app, self),

			bspump.declarative.DeclarativeTimeWindowAnalyzer(app, self,
				open("./bspump-declarative-twa.yaml").read()
			),

			bspump.common.NullSink(app, self)
		)


class Covid19Enricher(bspump.Processor):
	def process(self, context, event):
		return {
			'timestamp': datetime.datetime.strptime(event['Date'], "%m/%d/%Y"),
			'Case_type': event['\ufeffCase_Type'],
			'Cases': int(event['Cases']),
			'Country_Region': event['Country_Region'],
			'Province_State': event['Province_State']
		}


class MyApplication(bspump.BSPumpApplication):

	def __init__(self):
		super().__init__()
		svc = self.get_service("bspump.PumpService")
		self.PrimaryPipeline = Covid19Pipeline(self)
		svc.add_pipeline(self.PrimaryPipeline)

		self.PubSub.subscribe("Application.run!", self.on_run)
		self.PrimaryPipeline.PubSub.subscribe("bspump.pipeline.cycle_end!", self.on_end)

	def on_run(self, event_name):
		self.PrimaryPipeline.PubSub.publish("go!")

	def on_end(self, event_name, pipeline):
		self.stop()


if __name__ == '__main__':
	app = MyApplication()
	app.run()
