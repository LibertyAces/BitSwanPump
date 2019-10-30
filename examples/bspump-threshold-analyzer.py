import bspump
import bspump.common
import bspump.elasticsearch
import bspump.pipeline
import bspump.amqp
import bspump.random
import bspump.trigger
import bspump.analyzer
import numpy as np

import datetime



class CustomPipeline(bspump.Pipeline):
    def __init__(self, app, pipeline_id):
        super().__init__(app, pipeline_id)
        self.build(
            # bspump.amqp.AMQPSource(app, self, "AMQPConnection"),
            # bspump.common.BytesToStringParser(app,self),
            bspump.random.RandomSource(app, self,
                                       config={'number': 25, 'upper_bound': 5, 'field': 'server'}
                                       ).on(bspump.trigger.OpportunisticTrigger(app, chilldown_period=.1)),
            bspump.random.RandomEnricher(app, self, config={'field': 'duration', 'lower_bound': 1, 'upper_bound': 1500},
                                         id="RE0"),
            bspump.random.RandomEnricher(app, self, config={'field': '@timestamp',
                                                            'lower_bound': int(datetime.datetime.timestamp(datetime.datetime.now())-150),
                                                            'upper_bound': int(datetime.datetime.timestamp(datetime.datetime.now()))}, id="RE1"),
            MyThresholdAnalyzer(app,self,config={'event_attribute':'server', 'lower_bound':'-inf','upper_bound':145, 'load_event':'duration',}), # 'load':'duration'
            # bspump.common.PPrintSink(app, self),
            bspump.common.NullSink(app, self),
        )


class MyThresholdAnalyzer(bspump.analyzer.ThresholdAnalyzer):#TODO configure test analyzer

    ConfigDefaults = {

        'event_attribute': '',  # User defined value, e.g. server name
        'load_event': '',
        # if lower bound > upper bound: alarm is set when value is below lower bound, if lower bound != 0 and upper bound > lower_bound: alarm is set when value is out of bounds
        'lower_bound': 0,
        'upper_bound': 1000,
        'analyze_period': 5,

    }

    def __init__(self, app, pipeline, id=None, config=None):
        super().__init__(app, pipeline,id=id, config=config)

        self.EventAttribute = self.Config['event_attribute']
        self.Load = self.Config['load_event']
        self.Lower = float(self.Config['lower_bound'])
        self.Upper = float(self.Config['upper_bound'])
        self.WarmingUpLimit = int()

    # check if event contains related fields
    def predicate(self, context, event):
        if self.EventAttribute not in event:
            return False

        if "@timestamp" not in event:
            return False

        return True


    def evaluate(self, context, event):
        value = event[self.EventAttribute]  # server name e.g.
        time_stamp = event["@timestamp"]  # time stamp of the event

        self.row = self.TimeWindow.get_row_index(value)

        if self.row is None:
            self.row = self.TimeWindow.add_row(value)

        # find the column in timewindow matrix to fit in
        self.column = self.TimeWindow.get_column(time_stamp)
        if self.column is None:
            self.column = self.TimeWindow.get_column(time_stamp)
        # print(row, column, time_stamp, self.TimeWindow.Start, self.TimeWindow.End)

        # Load, creates histogram of occurences
        self.TimeWindow.Array[self.row, self.column] +=1


    def analyze(self):
        if self.TimeWindow.Array.shape[0] == 0:
            return

        self.WarmingUpLimit = self.TimeWindow.Columns - 1
        warming_up = self.TimeWindow.WarmingUpCount[self.row] <= self.WarmingUpLimit

        data = self.TimeWindow.Array[:, :]
        print(data)
        if self.Lower == 0 and np.any((data > self.Upper) & warming_up):
            print(self.alarm())
        elif self.Lower != 0 and self.Lower > self.Upper and np.any((data < self.Lower) & warming_up):  # subceedance
            print(self.alarm())
        elif self.Lower != 0 and self.Lower < self.Upper and (np.any((data < self.Lower) & warming_up) or
                                                                      np.any((data > self.Upper) & warming_up)):  # range (out of bounds)
            print(self.alarm())


    def alarm(self):
        alarm_result = str('Threshold has been subceeded / exceeded at {}'.format(str(datetime.datetime.now()
                                                                                      )[:-7].replace(" ", "T")))
        return alarm_result


if __name__=='__main__':
    app = bspump.BSPumpApplication()

    svc = app.get_service("bspump.PumpService")

    # Create amqp conn
    # svc.add_connection(
    #     bspump.amqp.AMQPConnection(app, "AMQPConnection"),
    # )

    # Constr & register pipeline
    svc.add_pipeline(
        CustomPipeline(app, "CustomPipeline"),
    )

    app.run()

