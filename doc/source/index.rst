.. BSPump Reference Documentation documentation master file, created by
   sphinx-quickstart on Wed Mar 27 11:05:14 2019.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.



Welcome to BSPump reference documentation!
==========================================================

.. toctree::
   :maxdepth: 1
   :caption: Reference

Application
===========

.. py:currentmodule:: bspump
.. py:class:: BSPumpApplication()

info about application

init
--------

.. py:currentmodule:: bspump
.. autofunction:: BSPumpApplication.__init__

.. py:method:: BSPumpApplication.__init__()

create_argument_parser
--------

.. py:method:: BSPumpApplication.create_argument_parser()

parse_arguments
--------

.. py:method:: BSPumpApplication.parse_arguments()

main
--------

.. py:method:: BSPumpApplication.main()

_on_signal_usr1
--------

.. py:method:: BSPumpApplication._on_signal_usr1()

BSPumpService
===========
.. py:currentmodule:: bspump
.. py:class:: BSPumpService()

init
--------

.. py:method:: BSPumpService.__init__()

locate
--------

.. py:method:: BSPumpService.locate()


add_pipeline
----------------

.. py:method:: BSPumpService.add_pipeline()

add_pipelines
----------------

.. py:method:: BSPumpService.add_pipelines()

del_pipeline
----------------

.. py:method:: BSPumpService.del_pipeline()

add_connection
----------------
.. py:method:: BSPumpService.add_connection()

add_connections
----------------

.. py:method:: BSPumpService.add_connections()

locate_connection
------------------------

.. py:method:: BSPumpService.locate_connection()

add_lookup
--------

.. py:method:: BSPumpService.add_lookup()

add_lookups
--------

.. py:method:: BSPumpService.add_lookups()

locate_lookup
--------

.. py:method:: BSPumpService.locate_lookup()

add_lookup_factory
--------

.. py:method:: BSPumpService.add_lookup_factory()

add_matrix
--------

.. py:method:: BSPumpService.add_matrix()

add_matrixes
--------

.. py:method:: BSPumpService.add_matrixes()

locate_matrix
--------

.. py:method:: BSPumpService.locate_matrix()

initialize
--------

.. py:method:: BSPumpService.initialize()

finalize
--------

.. py:method:: BSPumpService.finalize()


Pipeline
===========

.. py:currentmodule:: bspump
.. py:class:: Pipeline()

init
--------

.. py:method:: Pipeline.__init__()

time
--------

.. py:method:: Pipeline.time()

get_throttles
--------

.. py:method:: Pipeline.get_throttles()

_on_metrics_flush
--------

.. py:method:: Pipeline._on_metrics_flush()

is_error
--------

.. py:method:: Pipeline.is_error()

set_error
--------

.. py:method:: Pipeline.set_error()

handle_error
--------

.. py:method:: Pipeline.handle_error()

link
--------

.. py:method:: Pipeline.link()

unlink
--------

.. py:method:: Pipeline.unlink()

throttle
--------

.. py:method:: Pipeline.throttle()

evaluate ready
--------

.. py:method:: Pipeline._evaluate_ready()

evaluate ready
--------

.. py:method:: Pipeline._evaluate_ready()

ready
--------

.. py:method:: Pipeline.ready()

is_ready
--------

.. py:method:: Pipeline.is_ready()

do process
--------

.. py:method:: Pipeline._do_process()

inject
--------

.. py:method:: Pipeline.inject()

process
--------

.. py:method:: Pipeline.process()

create_eps_counter
--------

.. py:method:: Pipeline.create_eps_counter()

ensure_future
--------

.. py:method:: Pipeline.ensure_future()

_future_done
--------

.. py:method:: Pipeline._future_done()

set_source
--------

.. py:method:: Pipeline.set_source()

append_processor
--------

.. py:method:: Pipeline.append_processor()

remove_processor
--------

.. py:method:: Pipeline.remove_procesor()

insert_before
--------

.. py:method:: Pipeline.insert_before()

insert after
--------

.. py:method:: Pipeline.insert_after()

post add processor
--------

.. py:method:: Pipeline._post_add_processor()

build
--------

.. py:method:: Pipeline.build()

inter_processor
--------

.. py:method:: Pipeline.inter_processor()

locate_source
--------

.. py:method:: Pipeline.locate_source()

locate_connection
--------

.. py:method:: Pipeline.locate_connection()

locate_processor
--------

.. py:method:: Pipeline.locate_processor()

start
--------

.. py:method:: Pipeline.start()

stop
--------

.. py:method:: Pipeline.stop()

rest_get
--------

.. py:method:: Pipeline.rest_get()

PipeLineLogger
--------------
.. py:currentmodule:: bspump
.. py:class:: PipeLineLogger()

init
--------

.. py:method:: PipelineLogger.__init__()

handle
--------

.. py:method:: PipelineLogger.handle()

_format_time
--------

.. py:method:: PipelineLogger._format_time()


Lookup
===========
.. py:currentmodule:: bspump
.. py:class:: Lookup()

init
--------

.. py:method:: Lookup.__init__()

getitem
--------

.. py:method:: Lookup.__getitem__()

iter
--------

.. py:method:: Lookup.__iter__()

len
--------

.. py:method:: Lookup.__len__()

contains
--------

.. py:method:: Lookup.__contains__()

_create_provider
--------

.. py:method:: Lookup._create_provider()

time
--------

.. py:method:: Lookup.time()

ensure_future_update
--------

.. py:method:: Lookup.ensure_future_update()

_do_update
--------

.. py:method:: Lookup._do_update()

load
--------

.. py:method:: Lookup.load()

serialize
--------

.. py:method:: Lookup.serialize()

deserialize
--------

.. py:method:: Lookup.deserialize()

rest_get
--------

.. py:method:: Lookup.rest_get()

is_master
--------

.. py:method:: Lookup.is_master()

MappingLookup
--------

.. py:currentmodule:: bspump
.. py:class:: MappingLookup()

AsyncLookupMixin
--------

.. py:currentmodule:: bspump
.. py:class:: AsyncLookupMixin()

DictionaryLookup
---------------

.. py:currentmodule:: bspump
.. py:class:: DictionaryLookup()

init
--------

.. py:method:: DictionaryLookup.__init__()

get item
--------

.. py:method:: DictionaryLookup.__getitem__()

len
--------

.. py:method:: DictionaryLookup.__len__()

serialize
--------

.. py:method:: DictionaryLookup.serialize()

deserialize
--------

.. py:method:: DictionaryLookup.deserialize()

rest_get
--------

.. py:method:: DictionaryLookup.rest_get()

set
--------

.. py:method:: DictionaryLookup.set()

Source
===========
.. py:currentmodule:: bspump
.. py:class:: Source()

init
--------

.. py:method:: Source.__init__()

process
--------

.. py:method:: Source.process()

start
--------

.. py:method:: Source.start()

_main
--------

.. py:method:: Source._main()

stop
--------

.. py:method:: Source.stop()

restart
--------

.. py:method:: Source.restart()

main
--------

.. py:method:: Source.main()

stopped
--------

.. py:method:: Source.stopped()

locate_address
--------

.. py:method:: Source.locate_address()

rest_get
--------

.. py:method:: Source.rest_get()

repr
--------

.. py:method:: Source.__repr__()

consturct
--------

.. py:classmethod:: Source.construct()

TrigerSource
--------
.. py:currentmodule:: bspump
.. py:class:: TriggerSource()

init
--------

.. py:method:: TriggerSource.__init__()

time
--------

.. py:method:: TriggerSource.time()

on
--------

.. py:method:: TriggerSource.on()

main
--------

.. py:method:: TriggerSource.main()

cycle
--------

.. py:method:: TriggerSource.cycle()

rest_get
--------

.. py:method:: TriggerSource.rest_get()


Sink
===========
.. py:currentmodule:: bspump
.. py:class:: Sink()

Processor
===========
.. py:currentmodule:: bspump
.. py:class:: ProcessorBase()

init
--------

.. py:method:: ProcessorBase.__init__()

time
--------

.. py:method:: ProcessorBase.time()

constructed
--------

.. py:classmethod:::: ProcessorBase.construct()

process
--------

.. py:method:: ProcessorBase.process()

locate_address
--------

.. py:method:: ProcessorBase.locate_address()

rest_get
--------

.. py:method:: ProcessorBase.rest_get()

repr
--------

.. py:method:: ProcessorBase.__repr__()

Processor
--------

.. py:currentmodule:: bspump
.. py:class:: Processor

Generator
===========
.. py:currentmodule:: bspump
.. py:class:: Generator()

init
--------

.. py:method:: Generator.__init__()

set_depth
--------

.. py:method:: Generator.set_depth()

process
--------

.. py:method:: Generator.set_depth()

process
--------

.. py:method:: Generator.process()

generate
--------

.. py:method:: Generator.generate()

Connection
===========
.. py:currentmodule:: bspump
.. py:class:: Connection()

init
--------

.. py:method:: Connection.__init__()

time
--------

.. py:method:: Connection.time()

construct
--------

.. py:classmethod:::: Connection.consturct()

Lookup Provider
===========
.. py:currentmodule:: bspump
.. py:class:: LookupProviderABC()

load
--------

.. py:method:: LookupProviderABC.load()

LookupBatchProviderABC
--------

.. py:currentmodule:: bspump
.. py:class:: LookupBatchProviderABC()

Analyzer
===========
.. py:currentmodule:: bspump
.. py:class:: Analyzer()

init
^^^^^^

Analyzer
^^^^^^^^

init
--------

.. py:method:: Analyzer.__init__()

start_timer
--------

.. py:method:: Analyzer.start_timer()

analyze
--------

.. py:method:: Analyzer.analyze()

evaluate
--------

.. py:method:: Analyzer.evaluate()

predicate
--------

.. py:method:: Analyzer.predicate()

process
--------

.. py:method:: Analyzer.process()

on_clock_tick
--------

.. py:method:: Analyzer.on_clock_tick()

Analyzingsource
^^^^^^^

Anomaly TBD
===========
.. py:currentmodule:: bspump
.. py:class:: Anomaly()

**Technologies**
================

Kafka
===========

connection
----------
.. py:currentmodule:: bspump
.. py:class:: KafkaConnection()

Source
----------
.. py:currentmodule:: bspump
.. py:class:: KafkaSource()

Sink
----------
.. py:currentmodule:: bspump
.. py:class:: KafkaSink()

topic initializer
----------
.. py:currentmodule:: bspump
.. py:class:: KafkaTopicInitializer()

ElasticSearch
---------

Connection
----------
.. py:currentmodule:: bspump
.. py:class:: ElasticSearchBulk()


Lookup
----------
.. py:currentmodule:: bspump
.. py:class:: ElasticSearchLookup()

Sink
----------
.. py:currentmodule:: bspump
.. py:class:: ElasticSearchSink()

Source
----------
.. py:currentmodule:: bspump
.. py:class:: ElasticSearchSource()

Files
----------

CSV
----------


JSON
----------


AMQP
-----------

InfluxDB
-----------

Connection
----------
.. py:currentmodule:: bspump
.. py:class:: InfluxDBConnection()

Sink
----------
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
.. autoclass:: bspump.Application
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
