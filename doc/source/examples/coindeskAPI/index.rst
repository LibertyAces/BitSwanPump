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



Describe the purpose of the source

explain the parametr URL

explain the periodic trigger

explain sink and printsink

part3 - first processor
^^^^^^^^^^^^^^^^^^^^^^^

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

explain the purpose of the processor


Part4 - Custom processor
^^^^^^^^^^^^^^^^^^^^^^^^

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

