Escape From Tarkov Craft Profit Counter
=======================================


About
-----

In this example, I will show you


Source
------


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

Filter Processor
----------------


Dataframe to csv Processor
--------------------------


What next
---------

if you have a functional pipeline. You can do anything with the output data. For example, I created a simple
discord bot <link to a discord bot tutorial> that sends a message with the updated data.

image

The bot simply reads data from a csv file in data directory that is updated by the pipeline. Instead of this <reseni> you
can use database or any other way.


