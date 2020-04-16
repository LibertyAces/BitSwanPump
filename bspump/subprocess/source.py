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
		'ok_return_codes': '0', # TODO add example
	}


	def __init__(self, app, pipeline, *, id=None, config=None):
		super().__init__(app, pipeline, id=id, config=config)

		self.Command = str(self.Config["command"])
		assert self.Command, "`command` not set on " + self.__class__.__name__
		self._process = None
		# Get the list of OK return codes
		self.OKReturnCodes = [int(i.strip()) for i in self.Config["ok_return_codes"].split(',')]


	async def main(self):
		self._process = await asyncio.create_subprocess_shell(
			self.Command,
			shell=True,
			stdout=asyncio.subprocess.PIPE,
			stderr=asyncio.subprocess.DEVNULL,
			limit=self.Config.get("line_len_limit"),
		)
		# Check if process is running
		while self._process.returncode is None:
			await self.Pipeline.ready()
			event = await self._process.stdout.readline()
			await self.process(event)
		# Error message, when process has been terminated
		if self._process.returncode not in self.OKReturnCodes and self._process.returncode is not None:
			# Print error, wait a bit and retry again
			L.error("Command {} has exited with return code: {}".format(self.Command, self._process.returncode))
			await asyncio.sleep(5)
