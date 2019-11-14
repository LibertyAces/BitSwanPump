import logging
import subprocess

from ..abc.source import Source

L = logging.getLogger(__name__)


class SubProcessSource(Source):
	"""
	Sub-Process Source is capable of calling any command and fetch result from stdin as event

	Can be useful with commands like `tail -f`, `tshark -l -n -T ek -i wlan0` or others
	"""

	ConfigDefaults = {
		'command': '',
	}

	def __init__(self, app, pipeline, *, id=None, config=None):
		super().__init__(app, pipeline, id=id, config=config)

		self.Command = str(self.Config["command"])
		assert self.Command, "`command` not set on " + self.__class__.__name__

		self.Capture = subprocess.Popen(
			self.Command,
			shell=True,
			stdout=subprocess.PIPE,
			stderr=subprocess.DEVNULL,
		)

	async def main(self):
		while True:
			await self.Pipeline.ready()
			event = self.Capture.stdout.readline()
			await self.process(event)

	async def stop(self):
		self.Capture.kill()
		await super().stop()
