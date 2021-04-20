import logging

import bspump
import bspump.common
import bspump.elasticsearch
import bspump.file
import bspump.trigger

###

L = logging.getLogger(__name__)

###


class JSONPointerAccessProcessor(bspump.Processor):
	def process(self, context, event):
		return event.at_pointer("/actor/login")


class ListItemGenerator(bspump.Generator):
	async def generate(self, context, event, depth):
		for item in event:
			self.Pipeline.inject(context, item, depth)


class CySimdJSONExamplePipeline(bspump.Pipeline):

	"""
	Example usage of CySimdJsonParser, a JSON parser using a lightning fast cysimdjson library: https://github.com/TeskaLabs/cysimdjson, in a BitSwanPump pipeline
	"""

	def __init__(self, app, pipeline_id):
		super().__init__(app, pipeline_id)
		self.build(
			bspump.file.FileJSONSource(
				app,
				self,
				config={
					"path": "./data/large-file.json",
					"post": "noop",
				},
			).on(bspump.trigger.RunOnceTrigger(app)),
			SampleGenerator(app, self),
			bspump.common.DictToJsonBytesParser(app, self),
			bspump.common.CySimdJsonParser(app, self),
			JSONPointerAccessProcessor(app, self),
			bspump.common.PPrintSink(app, self),
		)


if __name__ == "__main__":
	app = bspump.BSPumpApplication()

	svc = app.get_service("bspump.PumpService")
	# Construct and register Pipeline
	pl = CySimdJSONExamplePipeline(
		app, "CySimdJSONExamplePipeline"
	)
	svc.add_pipeline(pl)
	pl.PubSub.publish("go!")
	app.run()
