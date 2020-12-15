#!/usr/bin/env python3
import logging

import bspump
import bspump.common
import bspump.file
import bspump.trigger

###

L = logging.getLogger(__name__)


###

class SamplePipeline(bspump.Pipeline):

    def __init__(self, app, pipeline_id):
        super().__init__(app, pipeline_id)
        # self.Sink = bspump.file.FileCSVSink(app, self, config={'path': './data/out1.csv'})

        self.build(
            bspump.file.FileJSONSource(
                app, self, config={
                    'path': './data/mithun.json',
                    'post': 'noop',
                }
            ).on(bspump.trigger.RunOnceTrigger(app)),
            ProcessorParse(app, self),
            bspump.common.PPrintSink(app, self),
        )
        # self.PubSub.subscribe("bspump.pipeline.cycle_end!", self.on_cycle_end)


class ProcessorParse(bspump.Processor):

    def __init__(self, app, pipeline):
        super().__init__(app, pipeline)

    def process(self, context, event):
        for recs in event:
            if 'id' not in event:
                return None
        output = event
        deviceid = event['id']
        imsi = event['IMSI']
        rsrp = event['RSRP0']
        rsrq = event['RSRQ']
        sinr = event['SINR']
        frequency = event['DLFrequency']
        rssi = event['RSSI']
        enbid = event['eNBID']
        if enbid == 'None':
            enbid = None
        pci = event['PCI']
        bandlock = event['LockBandList']
        cpe_params = [deviceid, imsi, rsrp, rsrq, sinr, frequency, rssi, enbid, pci, bandlock]
        #cpe_params1 = cpe_params
        return cpe_params

    def on_cycle_end(self, event_name, pipeline):
        '''
        This ensures that at the end of the file scan, the target file is closed
        '''
        self.Sink.rotate()


if __name__ == '__main__':
    app = bspump.BSPumpApplication()

    svc = app.get_service("bspump.PumpService")

    # Construct and register Pipeline
    pl = SamplePipeline(app, 'SamplePipeline')
    svc.add_pipeline(pl)

    app.run()
