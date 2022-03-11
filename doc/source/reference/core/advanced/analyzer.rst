Analyzer
===========
This is general analyzer interface, which can be the basement of different analyzers.
		`analyze_on_clock` enables analyzis by timer, which period can be set by `analyze_period` or
		`Config["analyze_period"]`.

		In general, the `Analyzer` contains some object, where it accumulates some information about events.
		Events go through analyzer unchanged, the information is recorded by `evaluate()` function.
		The internal object sometimes should be processed and sent somewhere (e.g. another pipeline),
		this process can be done by `analyze()` function, which can be triggered by time, pubsub or externally


.. py:currentmodule:: bspump

.. autoclass:: Analyzer
    :special-members: __init__
    :show-inheritance:

Analyzer construction
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

Analyzing source
~~~~~~~~~~~~~~~~
