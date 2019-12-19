import logging
import asyncio

from ..abc.source import Source

L = logging.getLogger(__name__)


class SubProcessSource(Source):
	"""
	Sub-Process Source is capable of calling any command and fetch result from stdin as event

	Can be useful with commands like `tail -f`, `tshark -l -n -T ek -i wlan0` or others
	"""

	ConfigDefaults = {
		'command': '',
		'line_len_limit': 2 ** 20,
	}

	def __init__(self, app, pipeline, *, id=None, config=None):
		super().__init__(app, pipeline, id=id, config=config)

		self.Command = str(self.Config["command"])
		assert self.Command, "`command` not set on " + self.__class__.__name__
		self._process = None

	async def main(self):
		self._process = await asyncio.create_subprocess_shell(
			self.Command,
			shell=True,
			stdout=asyncio.subprocess.PIPE,
			stderr=asyncio.subprocess.DEVNULL,
			limit=self.Config.get("line_len_limit"),
		)
		while True:
			await self.Pipeline.ready()
			event = await self._process.stdout.readline()
			await self.process(event)
