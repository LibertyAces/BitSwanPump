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
                                                            'lower_bound': int(datetime.datetime.timestamp(datetime.datetime.now())-5),
                                                            'upper_bound': int(datetime.datetime.timestamp(datetime.datetime.now()))}, id="RE1"),
            MyThresholdAnalyzer(app,self,config={'event_name':'server', 'lower_bound':50,'upper_bound':300, 'load':'duration',}), # 'load':'duration'
            # bspump.common.PPrintSink(app, self),
            bspump.common.NullSink(app, self),
        )


class MyThresholdAnalyzer(bspump.analyzer.ThresholdAnalyzer):#TODO configure test analyzer

    ConfigDefaults = {

        'event_name': '',  # User defined value, e.g. server name
        'load': '',
        # if lower bound > upper bound: alarm is set when value is below lower bound, if lower bound != 0 and upper bound > lower_bound: alarm is set when value is out of bounds
        'lower_bound': 0,
        'upper_bound': 1000,
        'analyze_period': 5, # Will start analyze method over defined period (in seconds)

    }

    def __init__(self, app, pipeline, id=None, config=None):
        super().__init__(app, pipeline,id=id, config=config)

        self.Event_name = self.Config['event_name']
        self.Load = self.Config['load']
        self.Lower = self.Config['lower_bound']
        self.Upper = self.Config['upper_bound']
        self.Row = []

        self.TimeWindow.zeros()  # initializing timewindow with zeros

    # check if event contains related fields
    def predicate(self, context, event):
        if self.Event_name not in event:
            return False

        if "@timestamp" not in event:
            return False

        return True

    def evaluate(self, context, event):
        value = event[self.Event_name]  # server name e.g.
        time_stamp = event["@timestamp"]  # time stamp of the event

        row = self.TimeWindow.get_row_index(value)

        if row is None:
            row = self.TimeWindow.add_row(value)
            if row not in self.Row:
                self.Row += [row]

        # find the column in timewindow matrix to fit in
        column = self.TimeWindow.get_column(time_stamp)
        if column is None:
            column = self.TimeWindow.get_column(time_stamp)

        # Load, creates histogram of occurences
        self.TimeWindow.Array[row, column] +=1

    def analyze(self):
        # checking an empty array
        if self.TimeWindow.Array.shape[0] == np.nan:
            return

        data = self.TimeWindow.Array[:, :]
        # Changing zero values to np.nan
        data[data == 0] = np.nan
        for i in self.Row:
            median_matrix_value = np.nanmedian(data[i, :])
            if self.Lower == 0 and median_matrix_value > self.Upper:  # exceedance
                print(self.alarm(median_matrix_value, i))
            elif self.Lower != 0 and self.Lower > self.Upper and median_matrix_value < self.Lower:  # subceedance
                print(self.alarm(median_matrix_value, i))
            elif self.Lower != 0 and self.Lower < self.Upper and (median_matrix_value < self.Lower or
                                                                  median_matrix_value > self.Upper):  # range (out of bounds)
                print(self.alarm(median_matrix_value, i))


    def alarm(self, value, id):
        alarm_result = str('Threshold has been subceeded / exceeded at {}'.format(str(datetime.datetime.now()
                                                                                      )[:-7].replace(" ", "T"))
                           + ' by value {}'.format(str(value))
                           + ' of server id: {}'.format(str(id)))
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

