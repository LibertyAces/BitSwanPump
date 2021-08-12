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