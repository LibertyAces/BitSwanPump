Coindesk API Example
====================

About
-----

In this example we will learn how get data from an HTTP like source in our example API.
We will be using HTTP Client Source for the API request.

The final pipeline will simply get data from the API request as a JSON,
covert it to python dictionary and output the data to Command Prompt.
Additinaly, I will show you how to create your own processor that in this example will enrich the data.

In this example we will be using API from ` Coindesk <https://www.coindesk.com/>`_ to get current price of Bitcoin.

The following code can be found
`here <https://github.com/LibertyAces/BitSwanPump/blob/feature/restructured-text/examples/bspump-http.py>`_
in our GitHub repo.

source and sink
^^^^^^^^^^^^^^^

In the code below you can see the basic structure of pipeline. The important part is the ``self.build()`` method where its
parameters are the single components of the pipeline. In this part we will use two main components each pipeline has to have
Source and Sink.

::
   class SamplePipeline(bspump.Pipeline):

       def __init__(self, app, pipeline_id):
           super().__init__(app, pipeline_id)

           self.build(
               bspump.http.HTTPClientSource(app, self, config={
                   'url': 'https://api.coindesk.com/v1/bpi/currentprice.json'
               }).on(bspump.trigger.PeriodicTrigger(app, 5)),
               bspump.common.PPrintSink(app, self),
           )

Source as figured from the name is source of data. In our example we will use a specific type of source. Because we need
to Pump data from API. We need to send request to the API to receive our data. This means that our source has to be
"triggered" when we get our response. For this reason we will be using so-called trigger source. More about Trigger
Source <<link TODO>>.

HTTP Client Source can have many configurations, but in our example we just need to specify our URL address, using
``config={'url': '<OUR URL>'}`` in the parameter of HTTP Client Source.

Because we are using Trigger Source. We need to specify which trigger we will be using. There are more types of
triggers, but in our example we will be using PeriodicTrigger, which triggers in time intervals specified in the
parameter. ``bspump.trigger.PeriodicTrigger(app, <<Time parameter in seconds>>))``

Each pipeline has to have sink. In our example we want to see the result of the data, so we will be using PPrintSink
which simply prints the data to the Command Prompt.

You can try to copy paste this chunk of code and try it yourself. Make use you have bspump module installed, if not you
can folow our guide <<todo link>>.

::

   #!/usr/bin/env python3
   import logging

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

part3 - first processor
^^^^^^^^^^^^^^^^^^^^^^^

After we have a functional pipeline. We can start adding the more interesing part, the processors. Processor is the
component which works with data in the event. In this example we will use a simple processor which only converts the
incoming JSON to python Dict type, which is much more easier to work with and it is clearer.

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

Processor is added simply by adding it to ``self.build()`` between source and sink.


Part4 - Custom processor
^^^^^^^^^^^^^^^^^^^^^^^^

Because most of your use cases will be unique, it is most likely that there will be no existing processor that could do
the work. So you will be forced to implement your own processor.

creating custom processor

Explain the template

::
   class EnrichProcessor(bspump.Processor):
    def __init__(self, app, pipeline, id=None, config=None):
        super().__init__(app, pipeline, id=None, config=None)

    def process(self, context, event):

        return event


Explain the reference of the procesor in self.build

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


Explain the final code

::
   class EnrichProcessor(bspump.Processor):
    def __init__(self, app, pipeline, id=None, config=None):
        super().__init__(app, pipeline, id=None, config=None)

    def convertUSDCZK(self, usd):
        return usd * 21.41 #outdated rate

    def process(self, context, event):
        czkPrice = str(self.convertUSDCZK(event["bpi"]["USD"]["rate_float"]))

        event["bpi"]["CZK"] = {
            "code": "CZK",
            "symbol": "K&#269;",
            "rate": ''.join((czkPrice[:3], ',', czkPrice[3:])),
            "description": "CZK",
            "rate_float": czkPrice
        }

        return event


.. literalinclude :: C:\Users\jachy\Documents\GitHub\BitSwanPump\examples\bspump-coindesk.py
   :language: python

Summarize what the whole pipeline does

part5 - Connecting to ES
^^^^^^^^^^^^^^^^^^^^^^^^

TODO

