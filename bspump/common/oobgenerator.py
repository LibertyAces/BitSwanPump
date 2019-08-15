import abc

import asyncio

from bspump.abc.generator import Generator


class OOBGenerator(Generator):
	"""
    OOBGenerator processes originally synchronous events "out-of-band" e.g. out of the synchronous processing within the pipeline.

    Specific implementation of OOBGenerator should implement the generate method to process events while performing long running (asynchronous) tasks such as HTTP requests.
    The long running tasks may enrich events with relevant information, such as output of external calculations.

    Example of generate method:

        async def generate(self, context, event):

            async with aiohttp.ClientSession() as session:
                async with session.get("https://example.com/resolve_color/{}".format(event.get("color_id", "unknown"))) as resp:
                    if resp.status != 200:
                        return event
                color = await resp.json()
                event["color"] = color

            await self.Pipeline.inject(context, output_event, depth)

"""
	pass
