Basics
=======

Pipeline
--------


.. py:currentmodule:: bspump

.. autoclass:: Pipeline
    :special-members: __init__
    :show-inheritance:


Pipeline construction
~~~~~~~~~~~~~~~~~~~~~

.. automethod:: bspump.Pipeline.set_source

.. automethod:: bspump.Pipeline.append_processor

.. automethod:: bspump.Pipeline.remove_processor

.. automethod:: bspump.Pipeline.insert_before

.. automethod:: bspump.Pipeline.insert_after

.. automethod:: bspump.Pipeline.build

.. automethod:: bspump.Pipeline.iter_processors


Other pipeline methods
~~~~~~~~~~~~~~~~~~~~~~

.. automodule:: bspump

.. automethod:: bspump.Pipeline.time

.. automethod:: bspump.Pipeline.get_throttles

.. automethod:: bspump.Pipeline._on_metrics_flush

.. automethod:: bspump.Pipeline.is_error()

.. automethod:: bspump.Pipeline.set_error()

.. automethod:: bspump.Pipeline.handle_error()

.. automethod:: bspump.Pipeline.link()

.. automethod:: bspump.Pipeline.unlink()

.. automethod:: bspump.Pipeline.throttle()

.. automethod:: bspump.Pipeline._evaluate_ready()

.. automethod:: bspump.Pipeline._evaluate_ready()

.. automethod:: bspump.Pipeline.ready()

.. automethod:: bspump.Pipeline.is_ready()

.. automethod:: bspump.Pipeline._do_process()

.. automethod:: bspump.Pipeline.inject()

.. automethod:: bspump.Pipeline.process()

.. automethod:: bspump.Pipeline.create_eps_counter()

.. automethod:: bspump.Pipeline.ensure_future()

.. automethod:: bspump.Pipeline.locate_source()

.. automethod:: bspump.Pipeline.locate_connection()

.. automethod:: bspump.Pipeline.locate_processor()

.. automethod:: bspump.Pipeline.start()

.. automethod:: bspump.Pipeline.stop()

.. automethod:: bspump.Pipeline.rest_get()




Connection
----------

.. py:currentmodule:: bspump

.. autoclass:: Connection
    :special-members: __init__
    :show-inheritance:

Connection construction
~~~~~~~~~~~~~~~~~~~~~~~

.. automethod:: bspump.Connection.time()

.. py:classmethod:::: Connection.consturct()



Source
------

.. py:currentmodule:: bspump

.. autoclass:: Source
    :special-members: __init__
    :show-inheritance:


Source construction
~~~~~~~~~~~~~~~~~~~

.. automethod:: bspump.Source.process()

.. automethod:: bspump.Source.start()

.. automethod:: bspump.Source._main()

.. automethod:: bspump.Source.stop()

.. automethod:: bspump.Source.restart()

.. automethod:: bspump.Source.main()

.. automethod:: bspump.Source.stopped()

.. automethod:: bspump.Source.locate_address()

.. automethod:: bspump.Source.rest_get()

.. automethod:: bspump.Source.__repr__()

.. automethod:: bspump.Source.construct()

Trigger source
~~~~~~~~~~~~~~

.. py:currentmodule:: bspump

.. autoclass:: TriggerSource
    :special-members: __init__
    :show-inheritance:


Trigger source methods
~~~~~~~~~~~~~~~~~~~~~~

.. automethod:: bspump.TriggerSource.time()

.. automethod:: bspump.TriggerSource.on()

.. automethod:: bspump.TriggerSource.main()

.. automethod:: bspump.TriggerSource.cycle()

.. automethod:: bspump.TriggerSource.rest_get()


Sink
----

.. py:currentmodule:: bspump

.. autoclass:: Sink
    :special-members: __init__
    :show-inheritance:


Processor
---------

.. py:currentmodule:: bspump

.. autoclass:: ProcessorBase
    :special-members: __init__
    :show-inheritance:


Processor construction
~~~~~~~~~~~~~~~~~~~~~~

.. automethod:: bspump.Processor.time()

.. automethod:: bspump.Processor.construct()

.. automethod:: bspump.Processor.process()

.. automethod:: bspump.Processor.locate_address()

.. automethod:: bspump.Processor.rest_get()

.. automethod:: bspump.Processor.__repr__()


Processor class
~~~~~~~~~~~~~~~

.. py:currentmodule:: bspump

.. autoclass:: Processor
    :special-members: __init__
    :show-inheritance:
