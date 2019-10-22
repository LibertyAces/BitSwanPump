import bspump
import bspump.common
import bspump.elasticsearch
import bspump.pipeline
import bspump.amqp
import bspump.random
import bspump.trigger
import bspump.analyzer

import datetime



class CustomAPMPipeline(bspump.Pipeline):
    def __init__(self, app, pipeline_id):
        super().__init__(app, pipeline_id)
        self.build(
            # bspump.amqp.AMQPSource(app, self, "AMQPConnection"),
            # bspump.common.BytesToStringParser(app,self),
            bspump.random.RandomSource(app, self,
                                       config={'number': 1000, 'upper_bound': 5, 'field': 'server'}
                                       ).on(bspump.trigger.OpportunisticTrigger(app, chilldown_period=.1)),
            bspump.random.RandomEnricher(app, self, config={'field': 'duration', 'lower_bound': 1, 'upper_bound': 1500},
                                         id="RE0"),
            bspump.random.RandomEnricher(app, self, config={'field': '@timestamp',
                                                            'lower_bound': int(datetime.datetime.timestamp(datetime.datetime.now())-5),
                                                            'upper_bound': int(datetime.datetime.timestamp(datetime.datetime.now()))}, id="RE1"),
            MyThresholdAnalyzer(app,self,config={'event_name':'server', 'lower_bound':0,'upper_bound':1000, 'load':'duration',}),
            # bspump.common.PPrintSink(app, self),
            bspump.common.NullSink(app, self),
        )


class MyThresholdAnalyzer(bspump.analyzer.ThresholdAnalyzer):#TODO configure test analyzer
    def __init__(self, app, pipeline, id=None, config=None):
        super().__init__(app, pipeline, id=id, config=config)

        # self.Split =
        # self._event_name =

    #TODO
    # def predicate(self, context, event):
        # var = str(event).split(self.Split)
        # for attr in var:
        # 	if self._event_name in attr:
        # 		print(attr)
        # 	else:
        # 		print(attr, type(attr), 'timestaaaaaamp')
        # if "@timestamp" in attr:
        # 	print(attr, 'timestaaaaaaamp')


if __name__=='__main__':
    app = bspump.BSPumpApplication()

    svc = app.get_service("bspump.PumpService")

    # Create amqp conn
    # svc.add_connection(
    #     bspump.amqp.AMQPConnection(app, "AMQPConnection"),
    # )

    # Constr & register pipeline
    svc.add_pipeline(
        CustomAPMPipeline(app, "CustomAPMPipeline"),
    )

    app.run()

