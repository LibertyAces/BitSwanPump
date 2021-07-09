Lookup
======
	Lookups serve for fast data searching in lists of key-value type. They can subsequently be localized and used
	in pipeline objects (processors and the like). Each lookup requires a statically or dynamically created value list.

	If the "lazy" parameter in the constructor is set to True, no load method is called and the user is expected
	to call it when necessary.

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

AsyncLookupMixin makes sure the value from the lookup is obtained asynchronously.
AsyncLookupMixin is to be used for every technology that is external to BSPump,
respective that require a connection to resource server such as SQL etc.


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
