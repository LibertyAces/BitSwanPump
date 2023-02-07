Apache Kafka
=============

Connection
----------

.. py:currentmodule:: bspump.kafka.connection

.. autoclass:: KafkaConnection
    :show-inheritance:


.. automethod:: bspump.kafka.connection.KafkaConnection.__init__()


connection Methods
~~~~~~~~~~~~~~~~~~

.. automethod:: bspump.kafka.connection.KafkaConnection.create_producer

.. automethod:: bspump.kafka.connection.KafkaConnection.create_consumer

.. automethod:: bspump.kafka.connection.KafkaConnection.get_bootstrap_servers

.. automethod:: bspump.kafka.connection.KafkaConnection.get_compression


Source
------

.. py:currentmodule:: bspump.kafka.source

.. autoclass:: KafkaSource
    :show-inheritance:

.. automethod:: bspump.kafka.source.KafkaSource.__init__()


Source Methods
~~~~~~~~~~~~~~

.. automethod:: bspump.kafka.source.KafkaSource.create_consumer

.. automethod:: bspump.kafka.source.KafkaSource.initialize_consumer

.. automethod:: bspump.kafka.source.KafkaSource.main


Sink
----

.. py:currentmodule:: bspump.kafka.sink

.. autoclass:: KafkaSink
    :show-inheritance:

.. automethod:: bspump.kafka.sink.KafkaSink.__init__()


Sink Methods
~~~~~~~~~~~~

.. automethod:: bspump.kafka.sink.KafkaSink.process


Key Filter Kafka
----------------

.. py:currentmodule:: bspump.kafka.keyfilter

.. autoclass:: KafkaKeyFilter
    :show-inheritance:

.. automethod:: bspump.kafka.keyfilter.KafkaKeyFilter.__init__()


.. automethod:: bspump.kafka.keyfilter.KafkaKeyFilter.process


Batch Sink
----------
.. py:currentmodule:: bspump.kafka.batchsink

.. autoclass:: KafkaBatchSink
    :show-inheritance:

.. automethod:: bspump.kafka.batchsink.KafkaBatchSink.__init__()


Batch Sink Methods
~~~~~~~~~~~~~~~~~~

.. automethod:: bspump.kafka.batchsink.KafkaBatchSink.process


Topic Initializer
-----------------

.. py:currentmodule:: bspump.kafka.topic_initializer

.. autoclass:: KafkaTopicInitializer
    :show-inheritance:

.. automethod:: bspump.kafka.topic_initializer.KafkaTopicInitializer.__init__()


topic initializer methods
~~~~~~~~~~~~~~~~~~~~~~~~~

.. automethod:: bspump.kafka.topic_initializer.KafkaTopicInitializer.include_topics

.. automethod:: bspump.kafka.topic_initializer.KafkaTopicInitializer.include_topics_from_file

.. automethod:: bspump.kafka.topic_initializer.KafkaTopicInitializer.include_topics_from_config

.. automethod:: bspump.kafka.topic_initializer.KafkaTopicInitializer.fetch_existing_topics

.. automethod:: bspump.kafka.topic_initializer.KafkaTopicInitializer.check_and_initialize

.. automethod:: bspump.kafka.topic_initializer.KafkaTopicInitializer.initialize_topics
