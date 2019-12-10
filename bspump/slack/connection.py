import aiohttp
import logging
import asyncio
import json
from ..abc.connection import Connection


L = logging.getLogger(__name__)



class SlackConnection(Connection):

	ConfigDefaults = {
		'hook_url': 'https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXXXXXXXXXX',
		'output_queue_max_size': 10,

	}

	def __init__(self, app, id=None, config=None):
		super().__init__(app, id=id, config=config)

		self.Url = self.Config['hook_url']

		self.Loop = app.Loop
		self.PubSub = app.PubSub

		self._output_queue_max_size = int(self.Config['output_queue_max_size'])
		self._output_queue = asyncio.Queue(loop=app.Loop, maxsize=self._output_queue_max_size + 1)
		self.LoaderTask = asyncio.ensure_future(self._loader(), loop=self.Loop)

		self.PubSub.subscribe("Application.exit!", self._on_exit)


	async def _on_exit(self, event_name):
		# Wait till the _loader() terminates
		pending = [self.LoaderTask]
		while len(pending) > 0:
			# By sending None via queue, we signalize end of life
			await self._output_queue.put(None)
			done, pending = await asyncio.wait(pending, return_when=asyncio.FIRST_COMPLETED)


	def consume(self, slack_message):
		slack_message = json.dumps(slack_message)
		self._output_queue.put_nowait(slack_message)

		if self._output_queue.qsize() == self._output_queue_max_size:
			self.PubSub.publish("SlackConnection.pause!", self)


	async def _loader(self):
		async with aiohttp.ClientSession() as session:
			while True:
				slack_message = await self._output_queue.get()
				if slack_message is None:
					break

				if self._output_queue.qsize() == self._output_queue_max_size - 1:
					self.PubSub.publish("SlackConnection.unpause!", self, asynchronously=True)

				async with session.post(self.Url, data=slack_message, headers={'content-type': 'application/json'}) as resp:
					resp_body = await resp.text()
					if resp.status != 200:
						L.error("Failed to send Slack message status:{} body:{}".format(resp.status, resp_body))

						# Requeue the message, wait a bit and try again
						self._output_queue.put_nowait(slack_message)
						await asyncio.sleep(5)
