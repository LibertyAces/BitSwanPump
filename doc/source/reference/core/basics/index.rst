Basics
=======

Pipeline
--------

.. py:currentmodule:: bspump
.. py:class:: Pipeline()

.. py:method:: Pipeline.__init__()


Pipeline construction
~~~~~~~~~~~~~~~~~~~~~

.. py:method:: Pipeline.set_source()

.. py:method:: Pipeline.append_processor()

.. py:method:: Pipeline.remove_procesor()

.. py:method:: Pipeline.insert_before()

.. py:method:: Pipeline.insert_after()

.. py:method:: Pipeline.build()

.. py:method:: Pipeline.inter_processor()


Other pipeline methods
~~~~~~~~~~~~~~~~~~~~~~

.. py:method:: Pipeline.time()

.. py:method:: Pipeline.get_throttles()

.. py:method:: Pipeline._on_metrics_flush()

.. py:method:: Pipeline.is_error()

.. py:method:: Pipeline.set_error()

.. py:method:: Pipeline.handle_error()

.. py:method:: Pipeline.link()

.. py:method:: Pipeline.unlink()

.. py:method:: Pipeline.throttle()

.. py:method:: Pipeline._evaluate_ready()

.. py:method:: Pipeline._evaluate_ready()

.. py:method:: Pipeline.ready()

.. py:method:: Pipeline.is_ready()

.. py:method:: Pipeline._do_process()

.. py:method:: Pipeline.inject()

.. py:method:: Pipeline.process()

.. py:method:: Pipeline.create_eps_counter()

.. py:method:: Pipeline.ensure_future()

You can use this method to schedule a future task that will be executed in a context of the pipeline.
        The pipeline also manages a whole lifecycle of the future/task, which means,
        it will collect the future result, trash it, and mainly it will capture any possible exception,
        which will then block the pipeline via set_error().

        If the number of futures exceeds the configured limit, the pipeline is throttled.

        :param coro:
        :return:


.. py:method:: Pipeline.locate_source()

.. py:method:: Pipeline.locate_connection()

.. py:method:: Pipeline.locate_processor()

.. py:method:: Pipeline.start()

.. py:method:: Pipeline.stop()

.. py:method:: Pipeline.rest_get()
