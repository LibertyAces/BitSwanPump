Basics
======

Basics covers the most fundamental components of a BSPump. We will start with the "backbone" of the BSPump, which is called a "pipeline".

Pipeline
--------

The pipeline class is responsible for construction of the BSPump pipeline itself. Its methods enable us to maintain
a working lifecycle of the system.

.. py:currentmodule:: bspump

.. autoclass:: Pipeline
    :show-inheritance:

.. automethod:: bspump.Pipeline.__init__()


Pipeline construction
~~~~~~~~~~~~~~~~~~~~~

The following are the core methods of the pipeline.

.. automethod:: bspump.Pipeline.build

.. automethod:: bspump.Pipeline.set_source

.. automethod:: bspump.Pipeline.append_processor

.. automethod:: bspump.Pipeline.remove_processor

.. automethod:: bspump.Pipeline.insert_before

.. automethod:: bspump.Pipeline.insert_after

.. automethod:: bspump.Pipeline.iter_processors


Other Pipeline Methods
~~~~~~~~~~~~~~~~~~~~~~

The additional methods below bring more features to the pipeline. However, many of them are very important and almost necessary.

.. automethod:: bspump.Pipeline.time

.. automethod:: bspump.Pipeline.get_throttles

.. automethod:: bspump.Pipeline.is_error

.. automethod:: bspump.Pipeline.set_error

.. automethod:: bspump.Pipeline.handle_error

.. automethod:: bspump.Pipeline.link

.. automethod:: bspump.Pipeline.unlink

.. automethod:: bspump.Pipeline.throttle

.. automethod:: bspump.Pipeline.ready

.. automethod:: bspump.Pipeline.is_ready

.. automethod:: bspump.Pipeline.inject

.. automethod:: bspump.Pipeline.process

.. automethod:: bspump.Pipeline.create_eps_counter

.. automethod:: bspump.Pipeline.ensure_future

.. automethod:: bspump.Pipeline.locate_source

.. automethod:: bspump.Pipeline.locate_connection

.. automethod:: bspump.Pipeline.locate_processor

.. automethod:: bspump.Pipeline.start

.. automethod:: bspump.Pipeline.stop


Source
------

.. py:currentmodule:: bspump.abc.source

.. autoclass:: Source
    :show-inheritance:

.. automethod:: bspump.abc.source.Source.__init__()


Source Construction
~~~~~~~~~~~~~~~~~~~

.. automethod:: bspump.abc.source.Source.process

.. automethod:: bspump.abc.source.Source.start

.. automethod:: bspump.abc.source.Source.stop

.. automethod:: bspump.abc.source.Source.restart

.. automethod:: bspump.abc.source.Source.main

.. automethod:: bspump.abc.source.Source.stopped

.. automethod:: bspump.abc.source.Source.locate_address

.. automethod:: bspump.abc.source.Source.construct

Trigger Source
~~~~~~~~~~~~~~

.. py:currentmodule:: bspump

.. autoclass:: TriggerSource
    :show-inheritance:

.. automethod:: bspump.TriggerSource.__init__()


Trigger Source Methods
~~~~~~~~~~~~~~~~~~~~~~

.. automethod:: bspump.TriggerSource.time

.. automethod:: bspump.TriggerSource.on

.. automethod:: bspump.TriggerSource.main

.. automethod:: bspump.TriggerSource.cycle


Processor
---------

.. py:currentmodule:: bspump

.. autoclass:: Processor
    :show-inheritance:

.. automethod:: bspump.Processor.__init__()


Processor Methods
~~~~~~~~~~~~~~~~~

.. automethod:: bspump.Processor.time

.. automethod:: bspump.Processor.construct

.. automethod:: bspump.Processor.process

.. automethod:: bspump.Processor.locate_address


Sink
----

Sink object serves as a final event destination within the pipeline given.
Subsequently, the event is dispatched/written into the system by the BSPump.

.. py:currentmodule:: bspump

.. autoclass:: Sink
    :show-inheritance:

.. automethod:: bspump.Sink.__init__()


Connection
----------

.. py:currentmodule:: bspump

.. autoclass:: Connection
    :show-inheritance:

.. automethod:: bspump.Connection.__init__()


Connection Methods
~~~~~~~~~~~~~~~~~~

.. automethod:: bspump.Connection.time

.. automethod:: Connection.construct

