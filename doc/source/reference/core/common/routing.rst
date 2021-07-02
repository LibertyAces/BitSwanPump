Routing
=======

Direct Source
-------------

.. py:currentmodule:: bspump.common

.. autoclass:: DirectSource
    :special-members: __init__
    :show-inheritance:


Direct Source
~~~~~~~~~~~~~

.. automethod:: bspump.common.DirectSource.put

.. automethod:: bspump.common.DirectSource.main


Internal Source
---------------

.. py:currentmodule:: bspump.common

.. autoclass:: InternalSource
    :special-members: __init__
    :show-inheritance:


Internal Source methods
~~~~~~~~~~~~~~~~~~~~~~~

.. automethod:: bspump.common.InternalSource.put

.. automethod:: bspump.common.InternalSource.put_async

.. automethod:: bspump.common.InternalSource.main

.. automethod:: bspump.common.InternalSource.rest_get


Router Mix In
-------------

.. py:currentmodule:: bspump.common.routing

.. autoclass:: RouterMixIn
    :special-members: __init__
    :show-inheritance:


Router Mix In methods
~~~~~~~~~~~~~~~~~~~~~

.. automethod:: bspump.common.routing.RouterMixIn._mixin_init

.. automethod:: bspump.common.routing.RouterMixIn.locate

.. automethod:: bspump.common.routing.RouterMixIn.unlocate

.. automethod:: bspump.common.routing.RouterMixIn.dispatch

.. automethod:: bspump.common.routing.RouterMixIn.route

.. automethod:: bspump.common.routing.RouterMixIn._on_target_pipeline_ready_change

.. automethod:: bspump.common.routing.RouterMixIn._on_internal_source_backpressure_ready_change


Router Sink
-----------

.. py:currentmodule:: bspump.common

.. autoclass:: RouterSink
    :special-members: __init__
    :show-inheritance:


Router Processor
----------------

.. py:currentmodule:: bspump.common

.. autoclass:: RouterProcessor
    :special-members: __init__
    :show-inheritance:

