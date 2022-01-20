How to connect to Elastic Search
================================

BSPump supports connection to Elastic Search platform. It is possible to connect to ES just in few lines of code.

Elastic Search Source
---------------------

TODO

how to take data from elastic

example

config

Elastic Search Sink
-------------------

You can use ES sink to store data for further analysis or visualizations using Kibana. The process to create ES sink is
simple.

Prerequisites
^^^^^^^^^^^^^

What you will need:

1. URL address for connection with Elastic Search
2. Configuration file
3. Register the service of ESConnection

Configuration File
^^^^^^^^^^^^^^^^^^

you will need to create`.conf` file using following syntax
::
    # Elasticsearch connection
    [connection:ESConnection]
    url=<<YOUR CONNECTION URL>>

    # Elasticsearch sink
    [pipeline:<<Name of your pipeline class>>:ElasticSearchSink]
    index=<<name of your index>>
    doctype=_doc

The configuration file can contain additional information depending on your implementation. However it is important that
it contains:

- index: name of the index that will be used to store your data in ES
- url: URL of your connection with ES
- doctype: type of the document, default is `_doc`


For more information visit our quickstart to using configs <link TODO>

Code example
^^^^^^^^^^^^

To create connection with Elastic Search you will need to do two things:

1. Add ElasticSearchSink component to `self.build` method of the pipeline class
2. create a service of your ES Connection.

You can implement your own ElasticSearch connection but the default connection will look like this:
::
    class SamplePipeline(bspump.Pipeline):

        def __init__(self, app, pipeline_id):
            super().__init__(app, pipeline_id)
            self.build(
                #Rest of the pipeline with source and processors
                #Adding ES Sink component
                bspump.elasticsearch.ElasticSearchSink(app, self, "ESConnection"),
            )

    if __name__ == '__main__':
        app = bspump.BSPumpApplication()
        svc = app.get_service("bspump.PumpService")

        #Part where you add the ESConnection service
        es_connection = bspump.elasticsearch.ElasticSearchConnection(app, "ESConnection")
        svc.add_connection(es_connection)

        svc.add_connection(
            bspump.kafka.KafkaConnection(app, "KafkaConnection")
        )

        svc.add_pipeline(
            KafkaPipeline(app, "KafkaPipeline")
        )

        app.run()

It is important to include `"ESConnection"` as a parameter in ElasticSearch connection and sink methods.


