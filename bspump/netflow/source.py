import logging
import subprocess

from ..abc.source import Source

L = logging.getLogger(__name__)


class NetFlowSource(Source):
	"""
	Source for capturing packets over network. Requires `tshark` to be installed - https://www.wireshark.org/docs/man-pages/tshark.html

	To allow non-root users to capture packets, run following command

		sudo usermod -a -G wireshark {username}

	"""

	ConfigDefaults = {
		'interface': 'wlan0',  # Should match one of the names listed in `tshark -D`
	}

	def __init__(self, app, pipeline, *, id=None, config=None):
		super().__init__(app, pipeline, id=id, config=config)

		self.Interface = str(self.Config["interface"])

		_command_check = ['tshark', '--version']
		_command_run = ['tshark', '-l', '-n', '-T', 'ek', '-i', self.Interface]
		try:
			subprocess.check_call(_command_check, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
		except FileNotFoundError:
			raise RuntimeError("Can not run `{}`. Is tshark installed?".format(" ".join(_command_check)))

		self.Capture = subprocess.Popen(
			_command_run,

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
