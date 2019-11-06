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
                                       config={'number': 250, 'lower_bound': 1,'upper_bound': 5, 'field': 'server'}
                                       ).on(bspump.trigger.OpportunisticTrigger(app, chilldown_period=.1)),
            bspump.random.RandomEnricher(app, self, config={'field': 'duration', 'lower_bound': 1, 'upper_bound': 1500},
                                         id="RE0"),
            bspump.random.RandomEnricher(app, self, config={'field': '@timestamp',
                                                            'lower_bound': int(datetime.datetime.timestamp(datetime.datetime.now())-250),
                                                            'upper_bound': int(datetime.datetime.timestamp(datetime.datetime.now()))}, id="RE1"),
            MyThresholdAnalyzer(app,self,config={'event_attribute':'server', 'lower_bound': 100, 'upper_bound':1450, 'event_value':'duration',}), # 'load':'duration'
            # bspump.common.PPrintSink(app, self),
            bspump.common.NullSink(app, self),
        )


class MyThresholdAnalyzer(bspump.analyzer.ThresholdAnalyzer):#TODO configure test analyzer

    ConfigDefaults = {

        'event_attribute': '',  # User defined value, e.g. server name
        'event_value': '',
        'lower_bound': '-inf',
        'upper_bound': 'inf',
        'analyze_period': 20,

    }

    def __init__(self, app, pipeline, id=None, config=None):
        super().__init__(app, pipeline,id=id, config=config)

        self.EventAttribute = self.Config['event_attribute']
        self.EventValue = self.Config['event_value']
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
        attribute = event[self.EventAttribute]  # server name e.g.
        time_stamp = event["@timestamp"]  # time stamp of the event

        self.row = self.TimeWindow.get_row_index(attribute)

        if self.row is None:
            self.row = self.TimeWindow.add_row(attribute)

        # find the column in timewindow matrix to fit in
        self.column = self.TimeWindow.get_column(time_stamp)
        if self.column is None:
            self.column = self.TimeWindow.get_column(time_stamp)
        # print(row, column, time_stamp, self.TimeWindow.Start, self.TimeWindow.End)

        # Create histogram of occurences
        self.TimeWindow.Array[self.row, self.column] +=1


    def analyze(self):
        if self.TimeWindow.Array.shape[0] == 0:
            return

        data = self.TimeWindow.Array
        self.WarmingUpLimit = self.TimeWindow.Columns - 1
        warming_up = np.resize(self.TimeWindow.WarmingUpCount <= self.WarmingUpLimit, data.shape)

        if (self.Lower == float('-inf') and self.Upper != float('inf')) and np.any((data >= self.Upper) & warming_up):
            x, y = np.where(data >= self.Upper)
            occurance = np.column_stack((x, y))
            value = data[x, y]
            print(self.alarm(occurance, value))

        elif (self.Lower != float('-inf') and self.Upper == float('inf')) and np.any((data <= self.Lower) & warming_up):
            x, y = np.where(data <= self.Lower)
            occurance = np.column_stack((x, y))
            value = data[x, y]
            print(self.alarm(occurance, value))

        elif (self.Lower != float('-inf') and self.Upper != float('inf')) and np.any(((data <= self.Lower) |
                                                                                      (data >= self.Upper)) & warming_up):
            x, y = np.where((data <= self.Lower) | (data >= self.Upper))
            occurance = np.column_stack((x, y))
            value = data[x, y]
            print(self.alarm(occurance, value))


    def alarm(self, occurance, value):
        alarm_result = str('Exceedance value is {} and'.format(str(value))+' it has appeared in {}'
                           .format(str(occurance)))
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

