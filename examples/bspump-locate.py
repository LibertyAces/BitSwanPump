"""
Example usage of the 'BSPumpService.locate' method.
"""

#!/usr/bin/env python3
import logging

import bspump
import bspump.common
import bspump.file
import bspump.trigger

###

L = logging.getLogger(__name__)

###


class BasicPipeline(bspump.Pipeline):

	def __init__(self, app, pipeline_id):
		super().__init__(app, pipeline_id)

		self.Source = bspump.file.FileCSVSource(app, self, config={'path': './data/sample.csv', 'delimiter': ';', 'post': 'noop'})
		self.Processor = bspump.common.PPrintProcessor(app, self)
		self.Sink = bspump.common.NullSink(app, self, id="BlackHoleSink")

		self.build(
			self.Source.on(bspump.trigger.RunOnceTrigger(app)),
			self.Processor,
			self.Sink
		)


if __name__ == '__main__':
	app = bspump.BSPumpApplication()
	svc = app.get_service("bspump.PumpService")
	svc.add_pipeline(BasicPipeline(app, 'SamplePipeline'))

	# Locate individual pipelines and components
	pipeline = svc.locate('SamplePipeline')  # To locate a pipeline, use its ID.
	processor = svc.locate('SamplePipeline.PPrintProcessor')  # To locate a processor, use ID of the pipeline and processor separated by '.'.
	sink = svc.locate('SamplePipeline.BlackHoleSink')  # The same applies for the sink, since its class is derived from processor base class.
	source = svc.locate('SamplePipeline.*FileCSVSource')  # To locate a source, add '*' before the source id.
	non_existing = svc.locate('SamplePipeline.NoSuchSinkExists')  # If no such component exists, the method returns None.

	print("\n\n")
	print("The list of located components:", end="\n\n")
	print("Pipeline: {}".format(pipeline.Id))
	print("Source: {}".format(source.Id))
	print("Processor: {}".format(processor.Id))
	print("Sink: {}".format(sink.Id), end="\n\n\n")

	app.run()
