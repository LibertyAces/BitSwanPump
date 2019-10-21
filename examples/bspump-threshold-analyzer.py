import bspump
import bspump.common
import bspump.elasticsearch
import bspump.pipeline
import bspump.amqp
# import bspump.kafka
import bspump.analyzer

import datetime
import random


class CustomAPMPipeline(bspump.Pipeline):
    def __init__(self, app, pipeline_id):
        super().__init__(app, pipeline_id)
        self.build(
            bspump.amqp.AMQPSource(app, self, "AMQPConnection"),
            bspump.common.BytesToStringParser(app, self),
            # bspump.common.JsonToDictParser(app, self),
            MyThresholdAnalyzer(app,self,config={'event_name':'host', 'threshold':[0,1000], 'level':'above','load':'',}),
            # bspump.common.PPrintSink(app, self),
            bspump.common.NullSink(app, self),
            # bspump.elasticsearch.ElasticSearchSink(app, self, "ESConnection"),
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

    # Create kafka, amqp and es conn
    svc.add_connections(
        # bspump.kafka.KafkaConnection(app, "KafkaConnection"),
        bspump.amqp.AMQPConnection(app, "AMQPConnection"),
        # bspump.elasticsearch.ElasticSearchConnection(app, "ESConnection"),# config={"bulk_out_max_size": 100,}),
    )

    # Constr & register pipelines
    svc.add_pipelines(
        # CustomKafkaMQPipeline(app, "CustomKafkaMQPipeline"),
        CustomAPMPipeline(app, "CustomAPMPipeline"),
    )

    app.run()

