Lookup
======

.. py:currentmodule:: bspump

.. autoclass:: Lookup
    :special-members: __init__
    :show-inheritance:


Lookup construction
~~~~~~~~~~~~~~~~~~~

.. automethod:: bspump.Lookup.__getitem__

.. automethod:: bspump.Lookup.__iter__

.. automethod:: bspump.Lookup.__len__

.. automethod:: bspump.Lookup.__contains__

.. automethod:: bspump.Lookup._create_provider

.. automethod:: bspump.Lookup.time

.. automethod:: bspump.Lookup.ensure_future_update

.. automethod:: bspump.Lookup._do_update

.. automethod:: bspump.Lookup.load

.. automethod:: bspump.Lookup.serialize

.. automethod:: bspump.Lookup.deserialize

.. automethod:: bspump.Lookup.rest_get

.. automethod:: bspump.Lookup.is_master


MappingLookup
--------------

.. py:currentmodule:: bspump

.. autoclass:: MappingLookup
    :special-members: __init__
    :show-inheritance:


AsyncLookupMixin
-----------------

.. py:currentmodule:: bspump

.. autoclass:: AsyncLookupMixin
    :special-members: __init__
    :show-inheritance:


DictionaryLookup
------------------

.. py:currentmodule:: bspump

.. autoclass:: DictionaryLookup
    :special-members: __init__
    :show-inheritance:


Dictionary Lookup methods
~~~~~~~~~~~~~~~~~~~~~~~~~

.. automethod:: bspump.DictionaryLookup.__getitem__

.. automethod:: bspump.DictionaryLookup.__len__

.. automethod:: bspump.DictionaryLookup.serialize

.. automethod:: bspump.DictionaryLookup.deserialize

.. automethod:: bspump.DictionaryLookup.rest_get

.. automethod:: bspump.DictionaryLookup.set


Lookup Provider
------------------

.. py:currentmodule:: bspump

.. autoclass:: LookupProviderABC
    :special-members: __init__
    :show-inheritance:


Lookup Provider methods
~~~~~~~~~~~~~~~~~~~~~~~

.. automethod:: bspump.LookupProviderABC.load()


LookupBatchProviderABC
------------------------

.. py:currentmodule:: bspump

.. autoclass:: LookupBatchProviderABC
    :special-members: __init__
    :show-inheritance:
