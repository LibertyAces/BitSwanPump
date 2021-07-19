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
    :special-members: __init__
    :show-inheritance:

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
    :special-members: __init__
    :show-inheritance:


ElasticSearch Connection methods
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. automethod:: bspump.elasticsearch.connection.ElasticSearchConnection.get_url

.. automethod:: bspump.elasticsearch.connection.ElasticSearchConnection.get_session

.. automethod:: bspump.elasticsearch.connection.ElasticSearchConnection.consume

.. automethod:: bspump.elasticsearch.connection.ElasticSearchConnection._start

.. automethod:: bspump.elasticsearch.connection.ElasticSearchConnection._on_exit

.. automethod:: bspump.elasticsearch.connection.ElasticSearchConnection._on_tick

.. automethod:: bspump.elasticsearch.connection.ElasticSearchConnection.flush

.. automethod:: bspump.elasticsearch.connection.ElasticSearchConnection.enqueue

.. automethod:: bspump.elasticsearch.connection.ElasticSearchConnection._loader


Elastic Search Bulk
~~~~~~~~~~~~~~~~~~~

.. py:currentmodule:: bspump.elasticsearch.connection

.. autoclass:: ElasticSearchBulk
    :special-members: __init__
    :show-inheritance:


Elastic Search Bulk methods
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. automethod:: bspump.elasticsearch.connection.ElasticSearchBulk.consume

.. automethod:: bspump.elasticsearch.connection.ElasticSearchBulk._get_data_from_items

.. automethod:: bspump.elasticsearch.connection.ElasticSearchBulk.upload

.. automethod:: bspump.elasticsearch.connection.ElasticSearchBulk.partial_error_callback

.. automethod:: bspump.elasticsearch.connection.ElasticSearchBulk.full_error_callback


Lookup methods
~~~~~~~~~~~~~~

.. automethod:: bspump.elasticsearch.lookup.ElasticSearchLookup._find_one
.. automethod:: bspump.elasticsearch.lookup.ElasticSearchLookup.get
.. automethod:: bspump.elasticsearch.lookup.ElasticSearchLookup.build_find_one_query
.. automethod:: bspump.elasticsearch.lookup.ElasticSearchLookup._count
.. automethod:: bspump.elasticsearch.lookup.ElasticSearchLookup.load
.. automethod:: bspump.elasticsearch.lookup.ElasticSearchLookup.construct


Sink methods
~~~~~~~~~~~~

.. automethod:: bspump.elasticsearch.sink.ElasticSearchSink.process
.. automethod:: bspump.elasticsearch.sink.ElasticSearchSink._connection_throttle


Data Feeder Methods
~~~~~~~~~~~~~~~~~~~

.. py:currentmodule:: bspump
.. py:class:: ElasticSearchBulk()

.. py:currentmodule:: bspump.elasticsearch

.. autoclass:: ElasticSearchSource
    :special-members: __init__
    :show-inheritance:
