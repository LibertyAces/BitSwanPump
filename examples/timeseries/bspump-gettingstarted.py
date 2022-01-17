#!/usr/bin/env python3
import logging

import bspump
import bspump.common
import bspump.http
import bspump.trigger

###

L = logging.getLogger(__name__)


###


class SamplePipeline(bspump.Pipeline):

    def __init__(self, app, pipeline_id):
        super().__init__(app, pipeline_id)

        self.build(
            bspump.http.HTTPClientSource(app, self, config={
                'url': 'https://api.coindesk.com/v1/bpi/currentprice.json'
            }).on(bspump.trigger.PeriodicTrigger(app, 3)),
            bspump.common.StdJsonToDictParser(app, self),
            bspump.common.PPrintSink(app, self),
        )


if __name__ == '__main__':
    app = bspump.BSPumpApplication()

    svc = app.get_service('bspump.PumpService')

    # Construct and register Pipeline
    pl = SamplePipeline(app, 'SamplePipeline')
    svc.add_pipeline(pl)

    app.run()
