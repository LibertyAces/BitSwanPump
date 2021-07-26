Routing
=======

Direct Source
-------------

.. py:currentmodule:: bspump.common

.. autoclass:: DirectSource
    :show-inheritance:

.. automethod:: bspump.common.DirectSource.__init__()


Direct Source
~~~~~~~~~~~~~

.. automethod:: bspump.common.DirectSource.put

.. automethod:: bspump.common.DirectSource.main


Internal Source
---------------

.. py:currentmodule:: bspump.common

.. autoclass:: InternalSource
    :show-inheritance:

.. automethod:: bspump.common.InternalSource.__init__()


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
    :show-inheritance:

.. automethod:: bspump.common.routing.RouterMixIn.__init__()


Router Mix In methods
~~~~~~~~~~~~~~~~~~~~~


.. automethod:: bspump.common.routing.RouterMixIn.locate

.. automethod:: bspump.common.routing.RouterMixIn.unlocate

.. automethod:: bspump.common.routing.RouterMixIn.dispatch

.. automethod:: bspump.common.routing.RouterMixIn.route


Router Sink
-----------

.. py:currentmodule:: bspump.common

.. autoclass:: RouterSink
    :show-inheritance:

.. automethod:: bspump.common.routing.RouterSink.__init__()


Router Processor
----------------

.. py:currentmodule:: bspump.common

.. autoclass:: RouterProcessor
    :show-inheritance:

.. automethod:: bspump.common.routing.RouterProcessor.__init__()