#!/usr/bin/env python3
import logging

import bspump
import bspump.common
import bspump.http
import bspump.trigger


class EnrichProcessor(bspump.Processor):
    def __init__(self, app, pipeline, id=None, config=None):
        super().__init__(app, pipeline, id=None, config=None)

    def convertUSDtoJPY(self, usd):
        return usd * 113.70  # outdated rate usd/jpy

    def process(self, context, event):
        jpyPrice = str(self.convertUSDtoJPY(event["bpi"]["USD"]["rate_float"]))

        event["bpi"]["JPY"] = {
            "code": "JPY",
            "symbol": "&yen;",
            "rate": ''.join((jpyPrice[:3], ',', jpyPrice[3:])),
            "description": "JPY",
            "rate_float": jpyPrice
        }

        return event

class SamplePipeline(bspump.Pipeline):

    def __init__(self, app, pipeline_id):
        super().__init__(app, pipeline_id)

        self.build(
            # Source that GET requests from the API source.
            bspump.http.HTTPClientSource(app, self, config={
                'url': 'https://api.coindesk.com/v1/bpi/currentprice.json'
                # Trigger that triggers the source every second (based on the method parameter)
            }).on(bspump.trigger.PeriodicTrigger(app, 5)),
            # Converts incoming json event to dict data type.
            bspump.common.StdJsonToDictParser(app, self),
            # Adds a CZK currency to the dict
            EnrichProcessor(app, self),
            bspump.common.StdDictToJsonParser(app,self),
            # prints the event to a console
            bspump.common.PPrintSink(app, self),
        )


if __name__ == '__main__':
    app = bspump.BSPumpApplication()

    svc = app.get_service("bspump.PumpService")

    # Construct and register Pipeline
    pl = SamplePipeline(app, 'SamplePipeline')
    svc.add_pipeline(pl)

    app.run()
