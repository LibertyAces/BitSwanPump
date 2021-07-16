ElasticSearch
==============

Source
------

ElasticSearchSource is using standard Elastic's search API to fetch data.

	**configs**

	*index* - Elastic's index (default is 'index-``*``').

	*scroll_timeout* - Timeout of single scroll request (default is '1m'). Allowed time units:
	https://www.elastic.co/guide/en/elasticsearch/reference/current/common-options.html#time-units

	**specific pamameters**

	*paging* - boolean (default is True)

	*request_body* - dictionary described by Elastic's doc:
	https://www.elastic.co/guide/en/elasticsearch/reference/current/search-request-body.html

	Default is:

.. code:: python

	default_request_body = {
		'query': {
			'bool': {
				'must': {
					'match_all': {}
				}
			}
		},
	}

.. py:currentmodule:: bspump.elasticsearch

.. autoclass:: ElasticSearchSource
    :show-inheritance:

.. automethod:: bspump.elasticsearch.source.ElasticSearchSource.__init__()

Source methods
~~~~~~~~~~~~~~

.. automethod:: bspump.elasticsearch.source.ElasticSearchSource.cycle

ElasticSearch Aggs Source
~~~~~~~~~~~~~~~~~~~~~~~~~

	ElasticSearchAggsSource is used for Elastic's search aggregations.

	**configs**

	*index*: - Elastic's index (default is 'index-``*``').

	**specific pamameters**

	*request_body*
	dictionary described by Elastic's doc:
	https://www.elastic.co/guide/en/elasticsearch/reference/current/search-request-body.html

	Default is:

.. code:: python

	default_request_body = {
		'query': {
			'bool': {
				'must': {
					'match_all': {}
				}
			}
		},
	}

.. py:currentmodule:: bspump.elasticsearch

.. autoclass:: ElasticSearchAggsSource
    :show-inheritance:

.. automethod:: bspump.elasticsearch.source.ElasticSearchAggsSource.__init__()

ElasticSearch Aggs Source methods
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. automethod:: bspump.elasticsearch.source.ElasticSearchAggsSource.cycle

.. automethod:: bspump.elasticsearch.source.ElasticSearchAggsSource.process_aggs

.. automethod:: bspump.elasticsearch.source.ElasticSearchAggsSource.process_buckets


ElasticSearch Connection
------------------------

ElasticSearchConnection allows your ES source, sink or lookup to connect to ElasticSearch instance

	usage:

.. code:: python


	# adding connection to PumpService
	svc = app.get_service("bspump.PumpService")
	svc.add_connection(
		bspump.elasticsearch.ElasticSearchConnection(app, "ESConnection")
	)

.. code:: python

	# pass connection name ("ESConnection" in our example) to relevant BSPump's object:

	self.build(
			bspump.kafka.KafkaSource(app, self, "KafkaConnection"),
			bspump.elasticsearch.ElasticSearchSink(app, self, "ESConnection")
	)


.. py:currentmodule:: bspump.elasticsearch

.. autoclass:: ElasticSearchConnection
    :show-inheritance:

.. automethod:: bspump.elasticsearch.connection.ElasticSearchConnection.__init__()

ElasticSearch Connection methods
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. automethod:: bspump.elasticsearch.connection.ElasticSearchConnection.get_url

.. automethod:: bspump.elasticsearch.connection.ElasticSearchConnection.get_session

.. automethod:: bspump.elasticsearch.connection.ElasticSearchConnection.consume

.. automethod:: bspump.elasticsearch.connection.ElasticSearchConnection.flush

.. automethod:: bspump.elasticsearch.connection.ElasticSearchConnection.enqueue



Elastic Search Bulk
~~~~~~~~~~~~~~~~~~~

.. py:currentmodule:: bspump.elasticsearch.connection

.. autoclass:: ElasticSearchBulk
    :show-inheritance:

.. automethod:: bspump.elasticsearch.connection.ElasticSearchBulk.__init__()

Elastic Search Bulk methods
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. automethod:: bspump.elasticsearch.connection.ElasticSearchBulk.consume

.. automethod:: bspump.elasticsearch.connection.ElasticSearchBulk.upload

.. automethod:: bspump.elasticsearch.connection.ElasticSearchBulk.partial_error_callback

.. automethod:: bspump.elasticsearch.connection.ElasticSearchBulk.full_error_callback


Lookup
------

.. py:currentmodule:: bspump.elasticsearch

.. autoclass:: ElasticSearchLookup
    :show-inheritance:

.. automethod:: bspump.elasticsearch.lookup.ElasticSearchLookup.__init__()

Lookup methods
~~~~~~~~~~~~~~

.. automethod:: bspump.elasticsearch.lookup.ElasticSearchLookup.get

.. automethod:: bspump.elasticsearch.lookup.ElasticSearchLookup.build_find_one_query

.. automethod:: bspump.elasticsearch.lookup.ElasticSearchLookup.load

.. automethod:: bspump.elasticsearch.lookup.ElasticSearchLookup.construct


Sink
----

.. py:currentmodule:: bspump.elasticsearch

.. autoclass:: ElasticSearchSink
    :show-inheritance:

.. automethod:: bspump.elasticsearch.sink.ElasticSearchSink.__init__()

Sink methods
~~~~~~~~~~~~

.. automethod:: bspump.elasticsearch.sink.ElasticSearchSink.process

.. automethod:: bspump.elasticsearch.sink.ElasticSearchSink._connection_throttle


Data Feeder Methods
~~~~~~~~~~~~~~~~~~~

.. automethod:: bspump.elasticsearch.data_feeder.data_feeder_create_or_index

.. automethod:: bspump.elasticsearch.data_feeder.data_feeder_create

.. automethod:: bspump.elasticsearch.data_feeder.data_feeder_index

.. automethod:: bspump.elasticsearch.data_feeder.data_feeder_update

.. automethod:: bspump.elasticsearch.data_feeder.data_feeder_delete





