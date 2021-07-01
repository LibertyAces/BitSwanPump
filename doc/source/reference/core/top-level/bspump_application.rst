Application
===========

.. py:currentmodule:: bspump

.. autoclass:: BSPumpApplication
    :special-members: __init__
    :show-inheritance:


Application construction
~~~~~~~~~~~~~~~~~~~~~~~~

.. automethod:: bspump.BSPumpApplication.create_argument_parser

.. automethod:: bspump.BSPumpApplication.create_argument_parser

.. automethod:: bspump.BSPumpApplication.parse_arguments

.. automethod:: bspump.BSPumpApplication.main

.. automethod:: bspump.BSPumpApplication._on_signal_usr1


BSPumpService
-------------

.. py:currentmodule:: bspump

.. autoclass:: BSPumpService
    :special-members: __init__
    :show-inheritance:

BSPumpService methods
~~~~~~~~~~~~~~~~~~~~~

.. automethod:: bspump.BSPumpService.locate

.. automethod:: bspump.BSPumpService.add_pipeline

.. automethod:: bspump.BSPumpService.add_pipelines

.. automethod:: bspump.BSPumpService.del_pipeline

.. automethod:: bspump.BSPumpService.add_connection

.. automethod:: bspump.BSPumpService.add_connections

.. automethod:: bspump.BSPumpService.locate_connection

.. automethod:: bspump.BSPumpService.add_lookup

.. automethod:: bspump.BSPumpService.add_lookups

.. automethod:: bspump.BSPumpService.locate_lookup

.. automethod:: bspump.BSPumpService.add_lookup_factory

.. automethod:: bspump.BSPumpService.add_matrix

.. automethod:: bspump.BSPumpService.add_matrixes

.. automethod:: bspump.BSPumpService.locate_matrix

.. automethod:: bspump.BSPumpService.initialize

.. automethod:: bspump.BSPumpService.finalize
