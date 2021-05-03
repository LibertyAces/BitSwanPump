#!/usr/bin/env python3
import logging
import time
import bspump
import bspump.avro
import bspump.common
import bspump.file
import bspump.trigger

###

L = logging.getLogger(__name__)

###


class LoadSource(bspump.TriggerSource):

    def __init__(self, app, pipeline, id=None, config=None):
        super().__init__(app, pipeline, id=id, config=config)
        self.Number = 100000

    async def cycle(self):
        stime = time.time()
        for i in range(0, 1000000):
            event = {
                'Country': "CZ",
                'Position': "1",
            }
            await self.process(event)
        etime = time.time()
        print("EPS: {:.0f}".format(self.Number / (etime - stime)))


class SamplePipeline(bspump.Pipeline):

    def __init__(self, app, pipeline_id):
        super().__init__(app, pipeline_id)

        self.sink = bspump.avro.AvroSink(app, self, config={
            'schema_file': '../data/sample-for-avro-schema.avsc',
            'file_name_template': '../data/sink_million{index}.avro',
        })

        self.build(
            LoadSource(app, self).on(bspump.trigger.PubSubTrigger(
                app, "Application.run!", pubsub=self.App.PubSub
            )),
            self.sink
        )

        self.PubSub.subscribe("bspump.pipeline.cycle_end!", self.on_cycle_end)

    def on_cycle_end(self, event_name, pipeline):
        self.sink.rotate()
        self.App.stop()


if __name__ == '__main__':
    app = bspump.BSPumpApplication()

    svc = app.get_service("bspump.PumpService")

    # Construct and register Pipeline
    pl = SamplePipeline(app, 'SamplePipeline')
    svc.add_pipeline(pl)

    app.run()