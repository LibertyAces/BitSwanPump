import bspump
import bspump.common
import bspump.pipeline
import bspump.random
import bspump.trigger
import bspump.analyzer

import numpy as np
import logging
import datetime

##

L = logging.getLogger(__name__)

##

class CustomPipeline(bspump.Pipeline):

    def __init__(self, app, pipeline_id):
        super().__init__(app, pipeline_id)
        self.build(
            bspump.random.RandomSource(app, self,
                                       config={'number': 15, 'lower_bound': 1,'upper_bound': 15, 'field': 'server'}
                                       ).on(bspump.trigger.OpportunisticTrigger(app, chilldown_period=.1)),

            bspump.random.RandomEnricher(app, self, config={'field': 'server_load', 'lower_bound': 1, 'upper_bound': 1500},
                                         id="RE0"),

            bspump.random.RandomEnricher(app, self, config={
                'field': '@timestamp', 'lower_bound': int(datetime.datetime.timestamp(datetime.datetime.now())-250),
                'upper_bound': int(datetime.datetime.timestamp(datetime.datetime.now()))}, id="RE1"),

            ExceedThresholdAnalyzer(app,self,config={'event_attribute': 'server', 'upper_bound': 1000,
                                                     'event_value': 'server_load', 'symptom_occurrence': 3,
                                                     'analyze_period': 60, }),

            bspump.common.NullSink(app, self),
        )


class ExceedThresholdAnalyzer(bspump.analyzer.ThresholdAnalyzer):

    """

    This is an example of threshold exceedance analyzer.
    User should define settings of analyzer in config.
    At least one of the bounds has to be set by the user.
    When bounds are not being set by the user, then default configuration is used.
    User should configure the alarm method.

...

    Config example:

    ExceedThresholdAnalyzer(app,self,config={'event_attribute': 'id', 'upper_bound': 1000, 'event_value': 'id_load',
                                             'symptom_occurrence': 2, 'analyze_period': 300, })

...

    Alarm example:

    def alarm(self, x, y, count, index):
        for c in range(0, count):
            position = np.column_stack((x[index-c], y[index-c]))
            L.warning('Threshold has been exceeded on those positions: {}'.format(str(position)))

    """

    def alarm(self, x, y, count, index):
        for c in range(0, count):
            L.warning('Threshold has been exceeded on those positions: {}'.format(str([x[index-c], y[index-c]])))


if __name__=='__main__':
    app = bspump.BSPumpApplication()

    svc = app.get_service("bspump.PumpService")

    svc.add_pipeline(
        CustomPipeline(app, "CustomPipeline"))

    app.run()

