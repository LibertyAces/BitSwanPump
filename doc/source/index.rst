.. BSPump Reference Documentation documentation master file, created by
   sphinx-quickstart on Wed Mar 27 11:05:14 2019.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to BSPump reference documentation!
==========================================================

.. toctree::
   :maxdepth: 1
   :caption: Contents:

**Core BSPump**
=============

Application
--------------
.. py:currentmodule:: bspump
.. py:class:: BSPumpApplication()

BSPumpService
---------------
.. py:currentmodule:: bspump
.. py:class:: BSPumpService()

Pipeline
---------------
.. py:currentmodule:: bspump
.. py:class:: Pipeline()

Lookup
---------------
.. py:currentmodule:: bspump
.. py:class:: Lookup()

Source
---------------
.. py:currentmodule:: bspump
.. py:class:: Source()

Sink
---------------
.. py:currentmodule:: bspump
.. py:class:: Sink()

Processor
---------------
.. py:currentmodule:: bspump
.. py:class:: Processor()

Generator
---------------
.. py:currentmodule:: bspump
.. py:class:: Generator()

Connection
---------------
.. py:currentmodule:: bspump
.. py:class:: Connection()

Lookup Provider
---------------
.. py:currentmodule:: bspump
.. py:class:: LookupProviderABC()

Analyzer
---------------
.. py:currentmodule:: bspump
.. py:class:: Analyzer()

Anomaly TBD
---------------
.. py:currentmodule:: bspump
.. py:class:: Anomaly()

**Technologies**
================

Kafka
-----

connection
^^^^^^^^^^
.. py:currentmodule:: bspump
.. py:class:: KafkaConnection()

Source
^^^^^^^^^^
.. py:currentmodule:: bspump
.. py:class:: KafkaSource()

Sink
^^^^^^^^^^
.. py:currentmodule:: bspump
.. py:class:: KafkaSink()

topic initializer
^^^^^^^^^^
.. py:currentmodule:: bspump
.. py:class:: KafkaTopicInitializer()

ElasticSearch
---------

Connection
^^^^^^^^^^
.. py:currentmodule:: bspump
.. py:class:: ElasticSearchBulk()


Lookup
^^^^^^^^^^
.. py:currentmodule:: bspump
.. py:class:: ElasticSearchLookup()

Sink
^^^^^^^^^^
.. py:currentmodule:: bspump
.. py:class:: ElasticSearchSink()

Source
^^^^^^^^^^
.. py:currentmodule:: bspump
.. py:class:: ElasticSearchSource()

Files
----------

CSV
^^^^^^^^^^


JSON
^^^^^^^^^^


AMQP
-----------

InfluxDB
-----------

Connection
^^^^^^^^^^
.. py:currentmodule:: bspump
.. py:class:: InfluxDBConnection()

Sink
^^^^^^^^^^
.. py:currentmodule:: bspump
.. py:class:: InfluxDBSink()

Sockets/IPC
------------

others
------------

**OLD REFERENCE**
========

BSpump
-------
.. automodule:: bspump.BSPumpApplication
    :members:
    :undoc-members:

Kafka
-------
.. automodule:: bspump.kafka
    :members:
    :undoc-members:

influxdb
-------
.. automodule:: bspump.influxdb
    :members:
    :undoc-members:

elastic
-------
.. automodule:: bspump.elasticsearch
    :members:
    :undoc-members:

declarative
-------
.. automodule:: bspump.declarative
    :members:
    :undoc-members:

declarative expression
-------
.. automodule:: bspump.declarative.expression
    :members:
    :undoc-members:

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
