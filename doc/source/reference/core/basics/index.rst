Basics
=======

Pipeline
--------

:meth:`Pipeline <bspump.Pipeline()>` is responsible for **data processing** in BSPump.
Individual :meth:`Pipeline <bspump.Pipeline()>` objects work **asynchronously** and **independently** of one another (provided dependence is not defined explicitly – for instance on a message source from some other pipeline) and can be triggered in unlimited numbers.
Each :meth:`Pipeline <bspump.Pipeline()>` is usually in charge of **one** concrete task.

There are three main components each pipeline has:

- :meth:`Source <bspump.Source()>`
- :meth:`Processor <bspump.Processor()>`
- :meth:`Sink <bspump.Sink()>`

Source connects different **data sources** with the :meth:`Pipeline <bspump.Pipeline()>` to be processed

.. image:: /images/pipeline.png
  :scale: 100
  :alt: Pipeline diagram

Multiple sources

A :meth:`Pipeline <bspump.Pipeline()>` can have multiple sources.
They are simply passed as a list of sources to a :meth:`Pipeline <bspump.Pipeline()>` `build()` method.

.. code:: python

   class MyPipeline(bspump.Pipeline):

      def __init__(self, app, pipeline_id):
         super().__init__(app, pipeline_id)
         self.build(
            [
               MySource1(app, self),
               MySource2(app, self),
               MySource3(app, self),
            ]
            bspump.common.NullSink(app, self),
         )
   :meta private:

The main component of the BSPump architecture is a so-called :meth:`Processor <bspump.Processor()>`.
This object **modifies**, **transforms** and **enriches** events.
Moreover, it is capable of **calculating metrics** and **creating aggregations**, **detecting anomalies** or react to known as well as unknown **system behaviour patterns**.

:meth:`Processors <bspump.Processor()>` differ as to their **functions** and all of them are aligned according to a predefined sequence in **pipeline objects**.
As regards working with data events, each :meth:`Pipeline <bspump.Pipeline()>` has its unique task.

:meth:`Processors <bspump.Processor()>` are passed as a **list** of :meth:`Processors <bspump.Processor()>` to a :meth:`Pipeline <bspump.Pipeline()>` `build()` method

.. code:: python

   class MyPipeline(bspump.Pipeline):

      def __init__(self, app, pipeline_id):
         super().__init__(app, pipeline_id)
         self.build(
            [
               MyProcessor1(app, self),
               MyProcessor2(app, self),
               MyProcessor3(app, self),
            ]
            bspump.common.NullSink(app, self),
         )
   :meta private:

Sink object serves as a **final event destination** within the pipeline given.
Subsequently, the event is dispatched/written into the system by the BSPump.

.. py:currentmodule:: bspump

.. autoclass:: Pipeline
    :special-members: __init__
    :show-inheritance:


Pipeline construction
~~~~~~~~~~~~~~~~~~~~~

.. automethod:: bspump.Pipeline.set_source

.. automethod:: bspump.Pipeline.append_processor

.. automethod:: bspump.Pipeline.remove_processor

.. automethod:: bspump.Pipeline.insert_before

.. automethod:: bspump.Pipeline.insert_after

.. automethod:: bspump.Pipeline.build

.. automethod:: bspump.Pipeline.iter_processors


Other pipeline methods
~~~~~~~~~~~~~~~~~~~~~~

.. automodule:: bspump

.. automethod:: bspump.Pipeline.time

.. automethod:: bspump.Pipeline.get_throttles

.. automethod:: bspump.Pipeline._on_metrics_flush

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


PipelineLogger
~~~~~~~~~~~~~~

.. py:currentmodule:: bspump.pipeline

.. autoclass:: PipelineLogger
    :special-members: __init__
    :show-inheritance:


.. automethod:: bspump.pipeline.PipelineLogger.handle()

.. automethod:: bspump.pipeline.PipelineLogger._format_time()


Source
------

Source is an **object** designed to obtain data from a predefined input.
The BSPump contains a lot of universally usable, specific source objects, which are capable of loading data from known data interfaces.
The BitSwan product further expands these objects by adding source objects directly usable for specific cases of use in industry field given.

Each source represent a coroutine/Future/Task that is running in the context of the main loop.
The coroutine method :meth:`main() <bspump.Source.main()>` contains an implementation of each particular source.

Source MUST await a :meth:`Pipeline <bspump.Pipeline()>` ready state prior producing the event.
It is acomplished by `await self.Pipeline.ready()` call.

.. py:currentmodule:: bspump

.. autoclass:: Source
    :special-members: __init__
    :show-inheritance:


Source construction
~~~~~~~~~~~~~~~~~~~

.. automethod:: bspump.Source.process()

.. automethod:: bspump.Source.start()

.. automethod:: bspump.Source._main()

.. automethod:: bspump.Source.stop()

.. automethod:: bspump.Source.restart()

.. automethod:: bspump.Source.main()

.. automethod:: bspump.Source.stopped()

.. automethod:: bspump.Source.locate_address()

.. automethod:: bspump.Source.rest_get()

.. automethod:: bspump.Source.__repr__()

.. automethod:: bspump.Source.construct()

Trigger source
~~~~~~~~~~~~~~

This is an abstract source class intended as a base for implementation of 'cyclic' sources such as file readers, SQL extractors etc.
You need to provide a trigger class and implement :meth:`cycle() <bspump.TriggerSource.cycle()>` method.

Trigger source will stop execution, when a :meth:`Pipeline <bspump.Pipeline()>` is cancelled (raises concurrent.futures.CancelledError).
This typically happens when a program wants to quit in reaction to a on the signal.

You also may overload the :meth:`main() <bspump.Source.main()>` method to provide additional parameters for a :meth:`cycle() <bspump.TriggerSource.cycle()>` method.

.. code:: python

	async def main(self):
		async with aiohttp.ClientSession(loop=self.Loop) as session:
			await super().main(session)


	async def cycle(self, session):
		session.get(...)


.. py:currentmodule:: bspump

.. autoclass:: TriggerSource
    :special-members: __init__
    :show-inheritance:


Trigger source methods
~~~~~~~~~~~~~~~~~~~~~~

.. automethod:: bspump.TriggerSource.time()

.. automethod:: bspump.TriggerSource.on()

.. automethod:: bspump.TriggerSource.main()

.. automethod:: bspump.TriggerSource.cycle()

.. automethod:: bspump.TriggerSource.rest_get()


Processor
---------

The main component of the BSPump architecture is a so called processor.
This object modifies, transforms and enriches events.
Moreover, it is capable of calculating metrics and creating aggregations, detecting anomalies or react to known as well as unknown system behavior patterns.

Processors differ as to their functions and all of them are aligned according to a predefined sequence in pipeline objects.
As regards working with data events, each pipeline has its own unique task.

.. py:currentmodule:: bspump

.. autoclass:: Processor
    :special-members: __init__
    :show-inheritance:


Processor construction
~~~~~~~~~~~~~~~~~~~~~~

.. automethod:: bspump.Processor.time()

.. automethod:: bspump.Processor.construct()

.. automethod:: bspump.Processor.process()

.. automethod:: bspump.Processor.locate_address()

.. automethod:: bspump.Processor.rest_get()

.. automethod:: bspump.Processor.__repr__()


Sink
----

Sink object serves as a final event destination within the pipeline given.
Subsequently, the event is dispatched/written into the system by the BSPump.

.. py:currentmodule:: bspump

.. autoclass:: Sink
    :special-members: __init__
    :show-inheritance:


Connection
----------

.. py:currentmodule:: bspump

.. autoclass:: Connection
    :special-members: __init__
    :show-inheritance:

Connection construction
~~~~~~~~~~~~~~~~~~~~~~~

.. automethod:: bspump.Connection.time()

.. py:classmethod:::: Connection.consturct()

