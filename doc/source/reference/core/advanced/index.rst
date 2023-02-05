Advanced
=========

BitSwan Pump provides more advanced Processors that can be used in a pipeline


Generator
---------

Generator object is used to generate one or multiple events in asynchronous way
	and pass them to following processors in the pipeline.
	In the case of Generator, user overrides `generate` method, not `process`.

	1.) Generator can iterate through an event to create (generate) derived ones and pass them to following processors.

	Example of a custom Generator class with generate method:

.. code:: python

		class MyGenerator(bspump.Generator):

			async def generate(self, context, event, depth):
				for item in event.items():
					self.Pipeline.inject(context, item, depth)

	2.) Generator can in the same way also generate completely independent events, if necessary.
	In this way, the generator processes originally synchronous events "out-of-band" e.g. out of the synchronous processing within the pipeline.

	Specific implementation of the generator should implement the generate method to process events while performing
	long running (asynchronous) tasks such as HTTP requests or SQL select.
	The long running tasks may enrich events with relevant information, such as output of external calculations.

	Example of generate method:

.. code:: python

		async def generate(self, context, event, depth):

			# Perform possibly long-running asynchronous operation
			async with aiohttp.ClientSession() as session:
				async with session.get("https://example.com/resolve_color/{}".format(event.get("color_id", "unknown"))) as resp:
					if resp.status != 200:
						return
					new_event = await resp.json()

			# Inject a new event into a next depth of the pipeline
			self.Pipeline.inject(context, new_event, depth)


.. py:currentmodule:: bspump

.. autoclass:: Generator
    :show-inheritance:

.. automethod:: bspump.Generator.__init__()


Generator Construction
~~~~~~~~~~~~~~~~~~~~~~

.. automethod:: bspump.Generator.set_depth

.. automethod:: bspump.Generator.process

.. automethod:: bspump.Generator.generate


Analyzer
--------

This is general analyzer interface, which can be the basement of different analyzers.
		`analyze_on_clock` enables analyzis by timer, which period can be set by `analyze_period` or
		`Config["analyze_period"]`.

		In general, the `Analyzer` contains some object, where it accumulates some information about events.
		Events go through analyzer unchanged, the information is recorded by `evaluate()` function.
		The internal object sometimes should be processed and sent somewhere (e.g. another pipeline),
		this process can be done by `analyze()` function, which can be triggered by time, pubsub or externally


.. py:currentmodule:: bspump

.. autoclass:: Analyzer
    :show-inheritance:

.. automethod:: bspump.Analyzer.__init__()


Analyzer Construction
~~~~~~~~~~~~~~~~~~~~~

.. automethod:: bspump.Analyzer.start_timer

Analyzer

The main function, which runs through the analyzed object.	Specific for each analyzer.
If the analyzed object is `Matrix`, it is not recommended to iterate through the matrix row by row (or cell by cell).
Instead use numpy fuctions. Examples:
1. You have a vector with n rows. You need only those row indeces, where the cell content is more than 10.	Use `np.where(vector > 10)`.
2. You have a matrix with n rows and m columns. You need to find out which rows
fully consist of zeros. use `np.where(np.all(matrix == 0, axis=1))` to get those row indexes.
Instead `np.all()` you can use `np.any()` to get all row indexes, where there is at least one zero.
3. Use `np.mean(matrix, axis=1)` to get means for all rows.
4. Usefull numpy functions: `np.unique()`, `np.sum()`, `np.argmin()`, `np.argmax()`.


.. automethod:: bspump.Analyzer.analyze

.. automethod:: bspump.Analyzer.evaluate

.. automethod:: bspump.Analyzer.predicate

.. automethod:: bspump.Analyzer.process

.. automethod:: bspump.Analyzer.on_clock_tick


Analyzing Source
~~~~~~~~~~~~~~~~


Lookup
------
	Lookups serve for fast data searching in lists of key-value type. They can subsequently be localized and used
	in pipeline objects (processors and the like). Each lookup requires a statically or dynamically created value list.

	If the "lazy" parameter in the constructor is set to True, no load method is called and the user is expected
	to call it when necessary.


.. py:currentmodule:: bspump

.. autoclass:: Lookup
    :show-inheritance:

.. automethod:: bspump.Lookup.__init__()


Lookup Construction
~~~~~~~~~~~~~~~~~~~

.. automethod:: bspump.Lookup.time

.. automethod:: bspump.Lookup.ensure_future_update

.. automethod:: bspump.Lookup.load

.. automethod:: bspump.Lookup.serialize

.. automethod:: bspump.Lookup.deserialize

.. automethod:: bspump.Lookup.is_master


MappingLookup
~~~~~~~~~~~~~

.. py:currentmodule:: bspump

.. autoclass:: MappingLookup
    :show-inheritance:

.. automethod:: bspump.MappingLookup.__init__()


Async Lookup Mixin
~~~~~~~~~~~~~~~~~~

AsyncLookupMixin makes sure the value from the lookup is obtained asynchronously.
AsyncLookupMixin is to be used for every technology that is external to BSPump,
respective that require a connection to resource server such as SQL etc.


.. py:currentmodule:: bspump.abc.lookup

.. autoclass:: AsyncLookupMixin
    :show-inheritance:


Dictionary Lookup
~~~~~~~~~~~~~~~~~

.. py:currentmodule:: bspump.abc.lookup

.. autoclass:: DictionaryLookup
    :show-inheritance:

.. automethod:: bspump.DictionaryLookup.__init__()


Dictionary Lookup Methods
~~~~~~~~~~~~~~~~~~~~~~~~~

.. automethod:: bspump.DictionaryLookup.__getitem__

.. automethod:: bspump.DictionaryLookup.__len__

.. automethod:: bspump.DictionaryLookup.serialize

.. automethod:: bspump.DictionaryLookup.deserialize

.. automethod:: bspump.DictionaryLookup.rest_get

.. automethod:: bspump.DictionaryLookup.set


Lookup Provider
~~~~~~~~~~~~~~~

.. py:currentmodule:: bspump.abc.lookupprovider

.. autoclass:: LookupProviderABC
    :show-inheritance:

.. automethod:: bspump.abc.lookup.LookupProviderABC.__init__()


Lookup Provider Methods
~~~~~~~~~~~~~~~~~~~~~~~

.. automethod:: bspump.abc.lookupprovider.LookupProviderABC.load


Lookup BatchProvider ABC
~~~~~~~~~~~~~~~~~~~~~~~~

.. py:currentmodule:: bspump.abc.lookupprovider

.. autoclass:: LookupBatchProviderABC
    :show-inheritance:

.. automethod:: bspump.abc.lookupprovider.LookupBatchProviderABC.__init__()


Anomaly
-------

.. py:currentmodule:: bspump

.. autoclass:: Anomaly
    :show-inheritance:

.. automethod:: bspump.abc.anomaly.Anomaly.__init__()
