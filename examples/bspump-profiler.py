import json
import logging
import time
import asab

import bspump
import bspump.common
import bspump.file
import bspump.http
import bspump.trigger
import requests


L = logging.getLogger(__name__)


class HTTPDelayProcessor(bspump.Processor):
	def process(self, context, event):
		# Delay 2 seconds on http request
		L.info("Sending HTTP request for 2+ seconds")
		response = requests.get(f"https://httpbin.org/delay/2?key={event['chartName']}")

		text = json.loads(response.text)
		event['chart_name'] = text.get('args', {}).get('key')
		return event


class SleepProcessor(bspump.Processor):
	def process(self, context, event):
		# Delay 2 seconds on http request
		time.sleep(2)
		return event


class ProfilingPipeline(bspump.Pipeline):
	# Enriches the event with location from ES lookup
	def __init__(self, app, pipeline_id=None):
		super().__init__(app, pipeline_id)

		self.Timer = asab.Timer(self, self.on_tick, autorestart=True)
		self.Timer.start(1)

		self.build(
			bspump.http.HTTPClientSource(app, self, config={
				'url': 'https://api.coindesk.com/v1/bpi/currentprice.json'
			}).on(bspump.trigger.PeriodicTrigger(app, 5)),
			bspump.common.JsonBytesToDictParser(app, self),
			HTTPDelayProcessor(app, self),
			SleepProcessor(app, self),
			bspump.common.NullSink(app, self)
		)

	async def on_tick(self):
		print(self.ProfilerCounter.rest_get())


if __name__ == '__main__':
	app = bspump.BSPumpApplication()

	svc = app.get_service("bspump.PumpService")

	my_pipeline = ProfilingPipeline(app, 'MyPipeline')
	svc.add_pipeline(my_pipeline)

	app.run()
