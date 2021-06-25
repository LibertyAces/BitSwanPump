#!/usr/bin/env python3
import logging
import bspump
import bspump.common
import bspump.elasticsearch
import bspump.file
import bspump.trigger
from bspump.lookup.memcachedlookup import Memcachedookup

###

L = logging.getLogger(__name__)


###

class FileCSVEnricher(bspump.Processor):
    """
	Index, can be specified in the event's context.

	If not specified, index will be in this case created by the specified rollover_mechanism.
	"""

    def process(self, context, event):
        current_time = int(self.App.time())
        # get memcached
        mem = Memcachedookup(self.App)
        # enrich with  time
        city = event["city"]
        if mem.rest_get(city) is None:
            L.debug("Setting data to memcached")
            mem.rest_set({city: current_time})
            event["cur_time"] = current_time
            return event
        else:
            L.debug("Fetching data from memcached")
            get_time = mem.rest_get(city)
            event["cur_time"] = get_time
            return event


class SamplePipeline(bspump.Pipeline):

    def __init__(self, app, pipeline_id):
        super().__init__(app, pipeline_id)
        self.build(
            bspump.file.FileCSVSource(app, self, config={
                'path': './data/city.csv',
                'delimiter': ';',
                'post': 'noop'
            }).on(bspump.trigger.RunOnceTrigger(app)),
            FileCSVEnricher(app, self),
            bspump.common.PPrintSink(app, self)
        )


if __name__ == '__main__':
    app = bspump.BSPumpApplication()

    svc = app.get_service("bspump.PumpService")
    pl = SamplePipeline(app, 'SamplePipeline')
    svc.add_pipeline(pl)
    pl.PubSub.publish("go!")

    app.run()
