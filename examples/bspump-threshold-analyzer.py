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
                                       config={'number': 5, 'lower_bound': 1,'upper_bound': 5, 'field': 'server'}
                                       ).on(bspump.trigger.OpportunisticTrigger(app, chilldown_period=.1)),

            bspump.random.RandomEnricher(app, self, config={'field': 'duration', 'lower_bound': 1, 'upper_bound': 1500},
                                         id="RE0"),

            bspump.random.RandomEnricher(app, self, config={
                'field': '@timestamp', 'lower_bound': int(datetime.datetime.timestamp(datetime.datetime.now())-250),
                'upper_bound': int(datetime.datetime.timestamp(datetime.datetime.now()))}, id="RE1"),

            ExceedThresholdAnalyzer(app,self,config={'event_attribute': 'server', 'upper_bound': 1000,
                                                         'event_value': 'duration',}),

            bspump.common.NullSink(app, self),
        )


class ExceedThresholdAnalyzer(bspump.analyzer.ThresholdAnalyzer):

    ConfigDefaults = {

        'event_attribute': '',
        'event_value': '',
        'lower_bound': '-inf',
        'upper_bound': 'inf',
        'analyze_period': 60,

    }

    def __init__(self, app, pipeline, id=None, config=None):
        super().__init__(app, pipeline,id=id, config=config)

        self.EventAttribute = self.Config['event_attribute']
        self.EventValue = self.Config['event_value']
        self.Lower = float(self.Config['lower_bound'])
        self.Upper = float(self.Config['upper_bound'])
        self.WarmingUpLimit = int()


    def predicate(self, context, event):
        if self.EventAttribute not in event:
            return False

        if "@timestamp" not in event:
            return False

        return True


    def evaluate(self, context, event):
        attribute = event[self.EventAttribute]
        time_stamp = event["@timestamp"]

        row = self.TimeWindow.get_row_index(attribute)
        if row is None:
            row = self.TimeWindow.add_row(attribute)

        column = self.TimeWindow.get_column(time_stamp)
        if column is None:
            column = self.TimeWindow.get_column(time_stamp)

        self.TimeWindow.Array[row, column] = event[self.EventValue]


    def analyze(self):
        if self.TimeWindow.Array.shape[0] == 0:
            return

        data = self.TimeWindow.Array
        self.WarmingUpLimit = self.TimeWindow.Columns - 1
        warming_up = np.resize(self.TimeWindow.WarmingUpCount <= self.WarmingUpLimit, data.shape)

        if np.any((data > self.Upper) & warming_up & (self.Lower == float('-inf') and self.Upper != float('inf'))):
            # Check where the exceedance values are stored and what numbers represents them
            x, y = np.where(data > self.Upper)
            occurance = np.column_stack((x, y))
            L.warning(str(self.alarm(occurance, data[x, y])))


    def alarm(self, occurance, value):
        alarm_result = str('Exceedance value is {} and'.format(str(value))+' it has appeared in {}'
                           .format(str(occurance)))
        return alarm_result


if __name__=='__main__':
    app = bspump.BSPumpApplication()

    svc = app.get_service("bspump.PumpService")

    svc.add_pipeline(
        CustomPipeline(app, "CustomPipeline"))

    app.run()

