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

.. autoclass:: Pipeline
    :members: set_source, append_processor, remove_processor, insert_before, insert_after, build, iter_processors
    :show-inheritance:
    :undoc-members:
    :hideclass::
    :exclude-members: Pipeline

.. automodule:: bspump
.. autofunction:: bspump.Pipeline.set_source

.. automethod:: bspump.Pipeline.set_source


Other pipeline methods
~~~~~~~~~~~~~~~~~~~~~~

.. automethod:: bspump.Pipeline.time()

.. automethod:: bspump.Pipeline.get_throttles()

.. automethod:: bspump.Pipeline._on_metrics_flush()

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

.. automethod:: bspump.Pipeline.time()

.. py:classmethod:::: Connection.consturct()



Source
------

.. py:currentmodule:: bspump

.. autoclass:: Source
    :special-members: __init__
    :show-inheritance:


Source construction
~~~~~~~~~~~~~~~~~~~

.. automethod:: bspump.Pipeline.process()

.. automethod:: bspump.Pipeline.start()

.. automethod:: bspump.Pipeline._main()

.. automethod:: bspump.Pipeline.stop()

.. automethod:: bspump.Pipeline.restart()

.. automethod:: bspump.Pipeline.main()

.. automethod:: bspump.Pipeline.stopped()

.. automethod:: bspump.Pipeline.locate_address()

.. automethod:: bspump.Pipeline.rest_get()

.. automethod:: bspump.Pipeline.__repr__()

.. automethod:: bspump.Pipeline.construct()

Triger source
~~~~~~~~~~~~~

.. py:currentmodule:: bspump

.. autoclass:: TriggerSource
    :special-members: __init__
    :show-inheritance:


Triger source methods
~~~~~~~~~~~~~~~~~~~~~

.. automethod:: bspump.Pipeline.__init__()

.. automethod:: bspump.Pipeline.time()

.. automethod:: bspump.Pipeline.on()

.. automethod:: bspump.Pipeline.main()

.. automethod:: bspump.Pipeline.cycle()

.. automethod:: bspump.Pipeline.rest_get()


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

.. automethod:: bspump.Pipeline.time()

.. automethod:: bspump.Pipeline.construct()

.. automethod:: bspump.Pipeline.process()

.. automethod:: bspump.Pipeline.locate_address()

.. automethod:: bspump.Pipeline.rest_get()

.. automethod:: bspump.Pipeline.__repr__()


Processor class
~~~~~~~~~~~~~~~

.. py:currentmodule:: bspump

.. autoclass:: Processor
    :special-members: __init__
    :show-inheritance:
