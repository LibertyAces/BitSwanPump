Weather API Example
===================
About
-----
In this example we will learn how get data from one or multiple HTTP sources using API request. In this case we cannot use basic
HTTPClientSource, because it returns data only from one API query, so to get data from different queries we will have
to define new source for this use case.

The final pipeline will get data from multiple API requests in one time as a JSON, convert it to python
dictionary and output the data to Command Prompt.

In this example we will be using API from `Open Weather <https://openweathermap.org/>`_ to get current weather data like temperature,
feels like temperature, pressure etc.

In this example we will use ``.conf`` file to store configuration for our pump. More about how to write configuration is
here :ref:`config`.

This is diagram how the finished pipeline will looks like

.. image:: weather_pipeline.png
    :width: 800
    :align: center
    :alt: Weather Pipeline Pic

Pipeline
--------

In the code below you can see the structure of pipeline which we need for this use case. The important part is the
``self.build()`` method where its parameters are the single components of the pipeline. Do not forget that every pipeline
requires both source and sink to function correctly.
::
    class SamplePipeline(bspump.Pipeline):

        def __init__(self, app, pipeline_id):
            super().__init__(app, pipeline_id)

            self.build(
                bspump.http.HTTPClientSource(app, self, config={
                'url': 'https://api.openweathermap.org/data/2.5/weather?q=<<LOCATION>>&units=metric&appid=<<YOUR PRIVATE API KEY>>'
                }).on(
                    bspump.trigger.PeriodicTrigger(app, 5)
                ),
                bspump.common.PPrintSink(app, self),
            )

Source as figured from the name is source of data. In our example we will use a specific type of source. Because we need
to Pump data from API. We need to send request to the API to receive our data. This means that our source has to be
“triggered” when we get our response. For this reason we will be using so-called trigger source. More about :ref:`trigger`.

Because we are using Trigger Source. We need to specify which trigger we will be using. There are more types of triggers,
but in our example we will be using PeriodicTrigger, which triggers in time intervals specified in the parameter.
``bspump.trigger.PeriodicTrigger(app, <<Time parameter in seconds>>))``

Each pipeline has to have a sink. In our example we want to see the result of the data, so we will be using PPrintSink
which simply prints the data to the Command Prompt.

You can try to copy paste this chunk of code and try it yourself. Make sure you have BSPump module installed, if
don't have follow our guide :ref:`bsmodule`.
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
                    'url': 'https://api.openweathermap.org/data/2.5/weather?q=<<LOCATION>>&units=metric&appid=<<YOUR PRIVATE API KEY>>'
                }).on(bspump.trigger.PeriodicTrigger(app, 5)),
                bspump.common.PPrintSink(app, self),
            )

    if __name__ == '__main__':
        app = bspump.BSPumpApplication()
        svc = app.get_service("bspump.PumpService")
        pl = SamplePipeline(app, 'SamplePipeline')
        svc.add_pipeline(pl)
        app.run()

Just simply rewrite ``<<LOCATION>>`` to whatever location you want to get weather data from and put your API key which you
will get after register on https://openweathermap.org/ to ``<<YOUR PRIVATE API KEY>>`` section.

Multiple location source
------------------------

In the code above the pump simply return data from one location. But in our use case we need to get data from multiple
location which means we need to get data from multiple API's URL. Now we define our specify trigger source.
::
    class LoadSource(bspump.TriggerSource):

        def __init__(self, app, pipeline, choice=None, id=None, config=None):
            super().__init__(app, pipeline, id=id, config=config)
            self.cities = ['London','New York','Berlin'] #List of cities

        async def cycle(self):
            async with aiohttp.ClientSession() as session:
                #goes through the list of cities and requests from API for each city
                for city in self.cities:
                    async with session.get(url=self.Config['url'].format(city=city, api_key=self.Config['api_key'])) as response:
                        event = await response.content.read()
                        await self.process(event)

You can see that in this example we are using ``self.Config`` method to get API key and url from configuration file. It is
good to have API key and url in configuration file, because when you will want to change it you just simply change it
in configuration file.

For example, create ``weather-pump.conf`` file and into that file you can copy past code below
::
    [pipeline:SamplePipeline:LoadSource]
    url = https://api.openweathermap.org/data/2.5/weather?q={city}&units=metric&appid={api_key}
    api_key = <<YOUR PRIVATE API KEY>>

When you will want to run your pump with configuration file you have to run it with ``-c`` switch. So after you finish your pump and you want to test it type for example ``python3 weather-pump.py -c weather-pump.conf`` to terminal.

You can change the list of cities to locations you wish. The important part of this source is ``async def cycle(self)``
method where we request API's url for every location from our list and process them in pipeline.

Just be sure that you import ``aiohttp`` package and you change ``HTTPClientSource`` with our new specified ``LoadSource``.
::
    #!/usr/bin/env python3

    import bspump
    import bspump.common
    import bspump.http
    import bspump.trigger
    import aiohttp


    class LoadSource(bspump.TriggerSource):

        def __init__(self, app, pipeline, choice=None, id=None, config=None):
            super().__init__(app, pipeline, id=id, config=config)
            self.cities = ['London','New York','Berlin'] #List of cities

        async def cycle(self):
            async with aiohttp.ClientSession() as session:
                #goes through the list of cities and requests from API for each city
                for city in self.cities:
                    async with session.get(url=self.Config['url'].format(city=city, api_key=self.Config['api_key'])) as response:
                        event = await response.content.read()
                        await self.process(event)


    class SamplePipeline(bspump.Pipeline):

        def __init__(self, app, pipeline_id):
            super().__init__(app, pipeline_id)

            self.build(
                LoadSource(app, self).on(
                    bspump.trigger.PeriodicTrigger(app, 5)
                ),
                bspump.common.PPrintSink(app, self),
            )

Add simple processor
--------------------

We can add some processor between source and sink. Processor is component which works with data in the event. In this
example we will use a simple processor which only converts the incoming JSON to python Dict type, which is much more
easier to work with and it is much more readable.

You can read more about :ref:`processor`.

The final pipeline structure will looks like this
::
    class SamplePipeline(bspump.Pipeline):

        def __init__(self, app, pipeline_id):
            super().__init__(app, pipeline_id)

            self.build(
                LoadSource(app, self).on(
                    bspump.trigger.PeriodicTrigger(app, 5)
                ),
                bspump.common.StdJsonToDictParser(app, self),
                bspump.common.PPrintSink(app, self),
            )

Connect to ES
-------------


More about Elastic search :ref:`esconnection`.
