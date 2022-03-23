.. _esconnection:

How to connect to Elastic Search
================================

BSPump supports the connection to Elastic Search platform. It is possible to connect to ES just in few lines of code.

Elastic Search Source
---------------------

You can use Elastic Search Source to take data from Elastic Search index for further analysis over them (e.g. in your pump).

Prerequisites
^^^^^^^^^^^^^

You can access ElasticSearch only if you have ElasticSearch already installed on your server or you can try to install it locally with
this tutorial :ref:`dockercompose`.

The process of taking data from Elastic Search index is simple, you will need few things.

What you will need:

1. URL address of your Elastic Search
2. Index with data
3. Configuration file
4. Register the service of ESConnection

Configuration File
^^^^^^^^^^^^^^^^^^

You will need to create `.conf` file with this configuration
::
    # ElasticSearch Source
    [pipeline:<<Name of your pipeline class>>:ElasticSearchSource]
    index=<<Name of your index>>

    # Elasticsearch connection
    [connection:ESConnection]
    url=<<Your ElasticSearch URL address>>

The configuration file can contain additional information depending on your implementation. It is essential to include:
- `index` : name of the index that will be used to get data from
- `url` : URL of your connection with ES

For more information visit our quickstart to using configs: :ref:`config`.

Code example
^^^^^^^^^^^^

To create a connection with Elastic Search you will need to do two things:

1. Add ElasticSearchSource component to `self.build` method of the pipeline class
2. Add trigger which take data from index every defined time
3. create a service of your ES Connection.

You can implement your own ElasticSearch connection but the default connection will look like this:
::
    class SamplePipeline(bspump.Pipeline):

    def __init__(self, app, pipeline_id):
        super().__init__(app, pipeline_id)
        self.build(
            # Adding ES Source component with trigger set up to trigger data every 5 seconds
            bspump.elasticsearch.ElasticSearchSource(app, self, "ESConnection").on(bspump.trigger.PeriodicTrigger(app, 5)),
            # Rest of the pipeline with source and processors
        )

    if __name__ == '__main__':
        app = bspump.BSPumpApplication()
        svc = app.get_service("bspump.PumpService")

        # Part where you add the ESConnection service
        es_connection = bspump.elasticsearch.ElasticSearchConnection(app, "ESConnection")
        svc.add_connection(es_connection)

        # Construct and register Pipeline
        pl = SamplePipeline(app, 'SamplePipeline')
        svc.add_pipeline(pl)

        app.run()

It is important to include `"ESConnection"` as a parameter in ElasticSearch connection and source methods.

Elastic Search Sink
-------------------

You can use Elastic Search sink to store data for further analysis or visualizations using Kibana.

Prerequisites
^^^^^^^^^^^^^

The process to create ES sink is simple and intuitive but you will need few things to start with.

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

The configuration file can contain additional information depending on your implementation. It is essential to include:

- `index` : name of the index that will be used to store your data in ES
- `url` : URL of your connection with ES
- `doctype` : type of the document, default is `_doc`


For more information visit our quickstart to using configs: :ref:`config`.

Code example
^^^^^^^^^^^^

To create a connection with Elastic Search you will need to do two things:

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

        app.run()

It is important to include `"ESConnection"` as a parameter in ElasticSearch connection and sink methods.


