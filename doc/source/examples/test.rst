OV05 BS-Testing Cofiguration Documentation
==========================================

Basic Pump Template
-------------------------
This is generic pump template you can use for your app.
::
    #!/usr/bin/env python3

    import bspump
    import bspump.common
    import bspump.http
    import asab

    # There is place for your processors

    class SamplePipeline(bspump.Pipeline):

        def __init__(self, app, pipeline_id):
            super().__init__(app, pipeline_id)

            self.build(
                # Source of data in pipeline triggered every 5 sec you can replace it for your desired source
                bspump.http.HTTPClientSource(app, self, config={
                   'url': 'https://api.coindesk.com/v1/bpi/currentprice.json'
                }).on(bspump.trigger.PeriodicTrigger(app, 5)),
                # Processor which convert JSON to Python dictionary
                bspump.common.StdJsonToDictParser(app, self),
                # Sink for printing data to terminal
                bspump.common.PPrintSink(app, self),
            )


    if __name__ == '__main__':
        app = bspump.BSPumpApplication()

        svc = app.get_service("bspump.PumpService")

        # Construct and register Pipeline
        pl = SamplePipeline(app, 'SamplePipeline')
        svc.add_pipeline(pl)

        app.run()

Blank app structure
-------------------
It is a good practice to have your app in blank app structure like in this tutorial TODO...

Elastic search connection
-------------------------
Import Elastic Search module from BSPump
::
    import bspump
    import bspump.common
    import bspump.http
    import bspump.elasticsearch
    import asab

Add Elastic Search connection to main function:
::
       if __name__ == '__main__':
        app = bspump.BSPumpApplication()

        svc = app.get_service("bspump.PumpService")

        # Adding Elastic Search connection here
        es_connection = bspump.elasticsearch.ElasticSearchConnection(app, "ESConnection")
        svc.add_connection(es_connection)

        # Construct and register Pipeline
        pl = SamplePipeline(app, 'SamplePipeline')
        svc.add_pipeline(pl)

        app.run()

Sink
^^^^
If you want to upload your data to Elastic Search index create ``.conf`` file with following config, change ``INDEX-NAME`` to your desired
index and ``PIPELINE-NAME`` to name of your pipline:
::
    # Elasticsearch connection
    [connection:ESConnection]
    url=http://10.17.168.197:9200

    # Elasticsearch sink
    [pipeline:PIPELINE-NAME:ElasticSearchSink]
    index=INDEX-NAME
    doctype=_doc

Then add ``bspump.elasticsearch.ElasticSearchSink`` to your pipeline like this:
::
    self.build(
                # Source of data in pipeline triggered every 5 sec you can replace it for your desired source
                bspump.http.HTTPClientSource(app, self, config={
                   'url': 'https://api.coindesk.com/v1/bpi/currentprice.json'
                }).on(bspump.trigger.PeriodicTrigger(app, 5)),
                # Processor which convert JSON to Python dictionary
                bspump.common.StdJsonToDictParser(app, self),
                # Sink to upload data to Elastic Search topic
                bspump.elasticsearch.ElasticSearchSink(app, self, "ESConnection"),
            )

Source
^^^^^^
If you want to get data from Elastic Search topic your ``.conf`` file have to looks like this, change ``INDEX-NAME`` tou your index
and ``PIPELINE-NAME`` to name of your pipeline:
::
    # Elasticsearch connection
    [connection:ESConnection]
    url=http://10.17.168.197:9200

    # Elasticsearch source
    [pipeline:PIPELINE-NAME:ElasticSearchSource]
    index=INDEX-NAME

Then add ``bspump.elasticsearch.ElasticSearchSource`` with ``PeriodicTrigger``
::
            self.build(
                # Elastic Search source which get data every 5 sec
                bspump.elasticsearch.ElasticSearchSource(app, self, "ESConnection").on(bspump.trigger.PeriodicTrigger(app, 5)),
                # Processor which convert JSON to Python dictionary
                bspump.common.StdJsonToDictParser(app, self),
                # Sink for printing data to terminal
                bspump.common.PPrintSink(app, self),
            )

Kafka Connection
----------------
Import Kafka module from BSPump
::
    import bspump
    import bspump.common
    import bspump.http
    import bspump.kafka
    import asab

Add Kafka connection to main function:
::
       if __name__ == '__main__':
        app = bspump.BSPumpApplication()

        svc = app.get_service("bspump.PumpService")

        # Adding Kafka connection here
        svc.add_connection(
        bspump.kafka.KafkaConnection(app, "KafkaConnection")
        )

        # Construct and register Pipeline
        pl = SamplePipeline(app, 'SamplePipeline')
        svc.add_pipeline(pl)

        app.run()

Sink
^^^^
If you want to stream your data in Kafka topic create ``.conf`` file with following config (change ``TOPIC-NAME`` to your topic
and ``PIPELINE-NAME`` to name of your pipeline):
::
    [connection:KafkaConnection]
    bootstrap_servers=10.17.168.197

    # Elasticsearch sink
    [pipeline:PIPELINE-NAME:KafkaSink]
    topic=TOPIC-NAME
Then add ``bspump.kafka.KafkaSink`` to your pipeline like this:
::
    self.build(
                # Source of data in pipeline triggered every 5 sec you can replace it for your desired source
                bspump.http.HTTPClientSource(app, self, config={
                   'url': 'https://api.coindesk.com/v1/bpi/currentprice.json'
                }).on(bspump.trigger.PeriodicTrigger(app, 5)),
                # Processor which convert JSON to Python dictionary
                bspump.common.StdJsonToDictParser(app, self),
                # Sink to upload data to Elastic Search topic
                bspump.kafka.KafkaSink(app, self, "KafkaConnection"),
            )