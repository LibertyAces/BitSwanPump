Aggregator
==========

Aggregation Strategy
--------------------

.. py:currentmodule:: bspump.common

.. autoclass:: AggregationStrategy
    :special-members: __init__
    :show-inheritance:


Aggregation Strategy methods
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. automethod:: bspump.common.AggregationStrategy.append

.. automethod:: bspump.common.AggregationStrategy.flush

.. automethod:: bspump.common.AggregationStrategy.is_empty


List Aggregation Strategy
-------------------------

.. py:currentmodule:: bspump.common

.. autoclass:: ListAggregationStrategy
    :special-members: __init__
    :show-inheritance:


List Aggregation Strategy methods
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. automethod:: bspump.common.ListAggregationStrategy.append

.. automethod:: bspump.common.ListAggregationStrategy.flush

.. automethod:: bspump.common.ListAggregationStrategy.is_empty


String Aggregation Strategy
---------------------------

.. py:currentmodule:: bspump.common

.. autoclass:: StringAggregationStrategy
    :special-members: __init__
    :show-inheritance:


String Aggregation Strategy methods
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. automethod:: bspump.common.StringAggregationStrategy.append

.. automethod:: bspump.common.StringAggregationStrategy.flush

.. automethod:: bspump.common.StringAggregationStrategy.is_empty


Aggregator
----------

.. py:currentmodule:: bspump.common

.. autoclass:: Aggregator
    :special-members: __init__
    :show-inheritance:


Aggregator
~~~~~~~~~~

.. automethod:: bspump.common.Aggregator._check_timeout

.. automethod:: bspump.common.Aggregator._check_periodic_flush

.. automethod:: bspump.common.Aggregator._on_application_stop

.. automethod:: bspump.common.Aggregator.flush

.. automethod:: bspump.common.Aggregator.process

.. automethod:: bspump.common.Aggregator.generate
