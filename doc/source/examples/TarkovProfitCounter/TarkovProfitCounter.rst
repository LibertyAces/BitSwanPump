Escape From Tarkov Craft Profit Counter
=======================================


About
-----

Pipeline in this example is inspired by game Escape from Tarkov. It is a realistic FPS game. Beside shooting enemies,
Players can earn and sell items in a game market which is driven by players themselves. The price of each item is changing in
real-time based on Demand-supply mechanics. Another important game mechanic is that players can create the items themself
in their specific stations. Items created and required for each crafts can be bought on the market, so players can earn
in-game money by producing the items. Because price of each item is not stable, some crafts are more profitable than others.
My idea was to take data from an API source that gives information of all available crafts players can do together with
price of each item. I will use this data to sort and analyze the data and output them in form that might help players know
which crafts is more profitable and suitable.

In this example I will show you a process of creating pipeline with a bit more complicated use. You will learn about
creating a source that enables us to use query in our API requests.


Source
------

First we have to create our source to pump the data to the pipeline. We will be using aiohttp library for our custom source.
We will start by creating our source class. As you can see in the code below.

::

    class IOHTTPSource(bspump.TriggerSource):
        def __init__(self, app, pipeline, choice=None, id=None, config=None):
            super().__init__(app, pipeline, id=id, config=config)

        async def cycle(self):
            async with aiohttp.ClientSession() as session:
                async with session.post('https://tarkov-tools.com/graphql', json={'query': query}) as response:
                    if response.status == 200:
                        event = await response.json()
                    else:
                        raise Exception("Query failed to run by returning code of {}. {}".format(response.status, query))
                    await self.process(event)

As you can see in the cycle method. We are using asynchronous functions for the API requests.

need for query

::
        query = """
    query {
      crafts {
        source
        duration
        rewardItems {
          quantity
          item {
            shortName
            lastLowPrice
          }
        }
        requiredItems {
          quantity
          item {
            shortName
            lastLowPrice
          }
        }
      }
    }
    """

You can try it yourself.

::

    #!/usr/bin/env python3
    import aiohttp
    import bspump
    import bspump.common
    import bspump.http
    import bspump.trigger
    import pandas as pd
    import bspump.file

    query = """
    query {
      crafts {
        source
        duration
        rewardItems {
          quantity
          item {
            shortName
            lastLowPrice
          }
        }
        requiredItems {
          quantity
          item {
            shortName
            lastLowPrice
          }
        }
      }
    }
    """

    class IOHTTPSource(bspump.TriggerSource):
        def __init__(self, app, pipeline, choice=None, id=None, config=None):
            super().__init__(app, pipeline, id=id, config=config)

        async def cycle(self):
            async with aiohttp.ClientSession() as session:
                async with session.post('https://tarkov-tools.com/graphql', json={'query': query}) as response:
                    if response.status == 200:
                        event = await response.json()
                    else:
                        raise Exception("Query failed to run by returning code of {}. {}".format(response.status, query))
                    await self.process(event)


    class SamplePipeline(bspump.Pipeline):

        def __init__(self, app, pipeline_id):
            super().__init__(app, pipeline_id)

            self.build(
                IOHTTPSource(app, self).on(bspump.trigger.PeriodicTrigger(app, 5)),
                bspump.common.PPrintProcessor(app,self),
                bspump.common.NullSink(app, self),
            )

You can copy the code above and try the pump yourself.

Filter Processor
----------------


::

    class FilterByStation(bspump.Processor):
        def __init__(self, app, pipeline, id=None, config=None):
            super().__init__(app, pipeline, id=None, config=None)

        def process(self, context, event):
            my_columns = ['station', 'name', 'output_price_item', 'duration', 'input_price_item', 'profit', 'profit_per_hour']
            df = pd.DataFrame(columns=my_columns)
            for item in event["data"]["crafts"]:
                duration = round((item["duration"])/60/60, ndigits=3)
                reward = item["rewardItems"][0]
                name_output = reward["item"]["shortName"]
                quantity = reward["quantity"]
                output_item_price = reward["item"]["lastLowPrice"]
                if output_item_price is None:  # checks for NULL values
                    output_item_price = 0
                output_price_item = quantity * int(output_item_price)
                station_name = item["source"]
                profit = 0
                profit_p_hour = 0
                input_price_item = 0
                for item2 in range(len(item["requiredItems"])):
                    required_item = item["requiredItems"][item2]
                    quantity_i = required_item["quantity"]
                    input_item = required_item["item"]["lastLowPrice"]
                    if input_item is None:
                        input_item = 0
                    price_of_input_item = input_item * quantity_i
                    input_price_item = input_price_item + price_of_input_item
                    profit = output_price_item - input_price_item
                    profit_p_hour = round(profit / duration, ndigits=3)
                df = df.append(
                    pd.Series([station_name,
                               name_output,
                               output_price_item,
                               duration,
                               input_price_item,
                               profit,
                               profit_p_hour],
                              index=my_columns), ignore_index=True)
                event = df
            return event


Dataframe to csv Processor
--------------------------

::

    class DataFrameToCSV(bspump.Processor):
        def __init__(self, app, pipeline, id=None, config=None):
            super().__init__(app, pipeline, id=None, config=None)

        def process(self, context, event):
            event.to_csv('./Data/TarkovData.csv', index=False)
            return event


What next
---------

if you have a functional pipeline. You can do anything with the output data. For example, I created a simple
discord bot <link to a discord bot tutorial> that sends a message with the updated data.

image

The bot simply reads data from a csv file in data directory that is updated by the pipeline. Instead of this <reseni> you
can use database or any other way.


