.. _coindesk:

Coindesk API Example
====================

About
-----

In this example we will learn how to extract any data from API. We will be using a HTTP Client Source for the API request.

In this example we will be using API from `Coindesk <https://www.coindesk.com/>`_ to get the current price of Bitcoin.

The final pipeline will simply get data from the API request as a JSON, covert it to python dictionary, and output the
data to Command Prompt. Additionally, I will show you how to create your own Processor to enrich
the data.

The following code can be found
`here <https://github.com/LibertyAces/BitSwanPump/blob/feature/restructured-text/examples/bspump-http.py>`_ in our GitHub repo.

A diagram of the final pipeline.

.. image:: coindesk_pipeline.png
   :width: 800
   :align: center
   :alt: Coindesk pipeline pic

Source and Sink
---------------

In the code below, you can see the basic structure of a pipeline. The important part is the ``self.build()`` method, where its
parameters are the single components of the pipeline. In this part we will use two main components each pipeline must contain:
Source and Sink.

::

   class SamplePipeline(bspump.Pipeline):

       def __init__(self, app, pipeline_id):
           super().__init__(app, pipeline_id)

           self.build(
               #Source of the pipeline
               bspump.http.HTTPClientSource(app, self, config={
                   'url': 'https://api.coindesk.com/v1/bpi/currentprice.json'
               }).on(bspump.trigger.PeriodicTrigger(app, 5)),
               #Sink of the pipeline
               bspump.common.PPrintSink(app, self),
           )



Source is a component that supplies the pipeline with data. In our example we will use a specific type of Source. Because we need
to Pump data from API, we need to send a request to the API to receive our data. This means that our Source has to regularly
and send the request using API. For this reason we will be using so-called Trigger Source. More about :ref:`trigger` .

HTTP Client Source can have many configurations, but in our example we just need to specify our URL address, using
``config={'url': '<OUR URL>'}``  as parameter in HTTP Client Source.

Because we are using Trigger Source, we need to specify which Trigger we will be using. There are many types of
Triggers, but in our example we will be using PeriodicTrigger, which triggers in time intervals specified in the
parameter. ``bspump.trigger.PeriodicTrigger(app, <<Time parameter in seconds>>))``

Each pipeline has to have Sink. In our example we want to see the result of the data, so we will be using PPrintSink,
which simply prints the data to the Command Prompt.

You can try to copy paste this chunk of code and try it yourself. Make use you have BSPump module installed for your Python, if not you
can follow our guide :ref:`bsmodule` .

::

   #!/usr/bin/env python3
   import bspump
   import bspump.common
   import bspump.http
   import bspump.trigger

   class SamplePipeline(bspump.Pipeline):

       def __init__(self, app, pipeline_id):
           super().__init__(app, pipeline_id)

           self.build(
               bspump.http.HTTPClientSource(app, self, config={
                   'url': 'https://api.coindesk.com/v1/bpi/currentprice.json'
               }).on(bspump.trigger.PeriodicTrigger(app, 5)),
               bspump.common.PPrintSink(app, self),
           )

   if __name__ == '__main__':
       app = bspump.BSPumpApplication()
       svc = app.get_service("bspump.PumpService")
       pl = SamplePipeline(app, 'SamplePipeline')
       svc.add_pipeline(pl)
       app.run()


Your First Processor
--------------------

After we have a functional pipeline, we can start with the more interesting part, Processors. The Processor is the
component which works with data of an event. In this example we will use a simple Processor, StdJsonToDictParser, which only converts the
incoming JSON to python Dict type, that is much easier to work with in python.

::

   class SamplePipeline(bspump.Pipeline):

       def __init__(self, app, pipeline_id):
           super().__init__(app, pipeline_id)

           self.build(
               bspump.http.HTTPClientSource(app, self, config={
                   'url': 'https://api.coindesk.com/v1/bpi/currentprice.json'
               }).on(bspump.trigger.PeriodicTrigger(app, 5)),
               bspump.common.StdJsonToDictParser(app, self),
               bspump.common.PPrintSink(app, self),
           )


this Processor is added simply by adding it to ``self.build()`` between Source and Sink.


Creating Custom Processor
-------------------------

Because a most of your use cases will be unique, it is most likely that there will be no existing Processor that could do
the work. Consequently, you will have to implement your own Processor.

Creating new Processor is not a complicated task. You will need to follow the basic structure of an general Processor.
You can simply copy-paste the code below:

::

   class EnrichProcessor(bspump.Processor):
    def __init__(self, app, pipeline, id=None, config=None):
        super().__init__(app, pipeline, id=None, config=None)

    def process(self, context, event):

        return event

This a sample processor class. The most important part of this processor class is the process method. This method will
be called when an event is passed to the Processor. As you can see, the default implementation of process method
returns the event `return event`. Event must be passed to the following component, another Processor or Sink.

If you wish to use your new Processor in our case `EnrichProcessor` You will need to reference it in `self.build` method.
You can do that simply by adding it to `self.build` parameters.

::

   class SamplePipeline(bspump.Pipeline):

       def __init__(self, app, pipeline_id):
           super().__init__(app, pipeline_id)

           self.build(
               bspump.http.HTTPClientSource(app, self, config={
                   'url': 'https://api.coindesk.com/v1/bpi/currentprice.json'
               }).on(bspump.trigger.PeriodicTrigger(app, 5)),
               bspump.common.StdJsonToDictParser(app, self),
               EnrichProcessor(app, self),
               bspump.common.PPrintSink(app, self),
           )


The last step is implementation. For our example, I created a simple script that takes the incoming event (python
dictionary that contains price of Bitcoin in USD, Euro, and Pounds) and adds a new branch with a Japanese yen. There is
also a new method `convertUSDtoJPY` that calculates the price of yen based on USD conversion rate
(Note: The exchange rate is outdated for sake of simplicity of this example).

::

   class EnrichProcessor(bspump.Processor):
    def __init__(self, app, pipeline, id=None, config=None):
        super().__init__(app, pipeline, id=None, config=None)

    def convertUSDtoJPY(self, usd):
        return usd * 113.70 #outdated rate usd/jpy

    def process(self, context, event):
        jpyPrice = str(self.convertUSDtoJPY(event["bpi"]["USD"]["rate_float"]))

        event["bpi"]["JPY"] = {
            "code": "JPY",
            "symbol": "&yen;",
            "rate": ''.join((jpyPrice[:3], ',', jpyPrice[3:])),
            "description": "JPY",
            "rate_float": jpyPrice
        }

        return event

When we add all parts together we get this functional code.

.. literalinclude :: BitSwanPump/examples/bspump-coindesk.py
   :language: python

To Summarize what we did in this example:

1. we created a sample pipeline with a Source and Sink
2. we added a new Processor that converts incoming events to python dictionary
3. we created a custom Processor that adds a information about Japanese currency to the incoming event and passes it to Sink .

Next steps
----------

You can change and modify the pipeline in any manner you want. For example, instead of using PPrintSink you can use our
Elastic Search Sink which loads the data to Elastic Search. Read more about :ref:`esconnection` .

