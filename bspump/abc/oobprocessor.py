import abc

from .generator import Generator


class OOBProcessor(Generator):
	"""
	OOBProcessor processes originally synchronous events "out-of-band" e.g. out of the synchronous processing within the pipeline.

	Specific implementation of OOBEEngine should implement the oob_process method to process events while performing long running (asynchronous) tasks such as HTTP requests.
	The long running tasks may enrich events with relevant information, such as output of external calculations.

	To utilize parallel processing of multiple events on worker coroutines, see the bspump.oob module.

	Example the processor:

	class MyOOBProcessor(bspump.OOBProcessor):

		async def oob_process(self, context, event):

			async with aiohttp.ClientSession() as session:
				async with session.get("https://example.com/resolve_color/{}".format(event.get("color_id", "unknown"))) as resp:
					if resp.status != 200:
						return event
				color = await resp.json()
				event["color"] = color

			return event

"""

	def process(self, context, event):

		def generate(oob_event):
			yield oob_event

		return generate(
			{
				"oob": {
					"coro": self.oob_process,
					"event": event,
				},
			}
		)

	@abc.abstractmethod
	async def oob_process(self, context, event):
		pass
