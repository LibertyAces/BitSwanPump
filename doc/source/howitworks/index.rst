How it works
============



Pipeline
--------

:meth:`Pipeline <bspump.Pipeline()>` is responsible for **data processing** in BSPump.
Individual :meth:`Pipeline <bspump.Pipeline()>` objects work **asynchronously** and **independently** of one another (provided dependence is not defined explicitly – for instance on a message source from some other pipeline) and can be triggered in unlimited numbers.
Each :meth:`Pipeline <bspump.Pipeline()>` is usually in charge of **one** concrete task.

Pipeline has three main components:

- :meth:`Source <bspump.Source()>`
- :meth:`Processor <bspump.Processor()>`
- :meth:`Sink <bspump.Sink()>`



.. image:: /images/pipeline.png
  :scale: 100
  :alt: Pipeline diagram

Source connects different **data sources** with the :meth:`Pipeline <bspump.Pipeline()>` to be processed

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
Subsequently, the event is dispatched/written into the system by the BSPump

Source
------

Source is an **object** designed to obtain data from a predefined input.
The BSPump contains a lot of universally usable, specific source objects, which are capable of loading data from known data interfaces.
The BitSwan product further expands these objects by adding source objects directly usable for specific cases of use in industry field given.

Each source represent a coroutine/Future/Task that is running in the context of the main loop.
The coroutine method :meth:`main() <bspump.Source.main()>` contains an implementation of each particular source.

Source MUST await a :meth:`Pipeline <bspump.Pipeline()>` ready state prior producing the event.
It is acomplished by `await self.Pipeline.ready()` call.

Trigger Source
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


Processor
---------

The main component of the BSPump architecture is a so called processor.
This object modifies, transforms and enriches events.
Moreover, it is capable of calculating metrics and creating aggregations, detecting anomalies or react to known as well as unknown system behavior patterns.

Processors differ as to their functions and all of them are aligned according to a predefined sequence in pipeline objects.
As regards working with data events, each pipeline has its own unique task.