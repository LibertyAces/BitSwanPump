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
    :special-members: __init__
    :show-inheritance:


Source methods
~~~~~~~~~~~~~~

.. automethod:: bspump.Source.ElasticSearchSource.cycle

.. automethod:: bspump.ElasticSearchAggsSource.cycle

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

.. automethod:: bspump.ElasticSearchAggsSource.cycle

.. automethod:: bspump.ElasticSearchAggsSource.process_aggs

.. automethod:: bspump.ElasticSearchAggsSource.process_buckets


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

.. automethod:: bspump.ElasticSearchConnection.get_url

.. automethod:: bspump.ElasticSearchConnection.get_session

.. automethod:: bspump.ElasticSearchConnection.consume

.. automethod:: bspump.ElasticSearchConnection._start

.. automethod:: bspump.ElasticSearchConnection._on_exit

.. automethod:: bspump.ElasticSearchConnection._on_tick

.. automethod:: bspump.ElasticSearchConnection.flush

.. automethod:: bspump.ElasticSearchConnection.enqueue

.. automethod:: bspump.ElasticSearchConnection._loader


Elastic Search Bulk
~~~~~~~~~~~~~~~~~~~

.. py:currentmodule:: bspump.elasticsearch

.. autoclass:: ElasticSearchBulk
    :special-members: __init__
    :show-inheritance:


Elastic Search Bulk methods
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. automethod:: bspump.ElasticSearchBulk.consume

.. automethod:: bspump.ElasticSearchBulk._get_data_from_items

.. automethod:: bspump.ElasticSearchBulk.upload

.. automethod:: bspump.ElasticSearchBulk.partial_error_callback

.. automethod:: bspump.ElasticSearchBulk.full_error_callback


Lookup
------

.. py:currentmodule:: bspump.elasticsearch

.. autoclass:: ElasticSearchLookup
    :special-members: __init__
    :show-inheritance:


Lookup methods
~~~~~~~~~~~~~~

Sink
----

.. py:currentmodule:: bspump.elasticsearch

.. autoclass:: ElasticSearchSink
    :special-members: __init__
    :show-inheritance:


Sink methods
~~~~~~~~~~~~


Data Feeder Methods
~~~~~~~~~~~~~~~~~~~

.. py:currentmodule:: bspump
.. py:class:: ElasticSearchBulk()

.. py:currentmodule:: bspump.elasticsearch

.. autoclass:: ElasticSearchSource
    :special-members: __init__
    :show-inheritance:
