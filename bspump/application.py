import signal
import sys

import asab

from .service import BSPumpService
from .__version__ import __version__, __build__


class BSPumpApplication(asab.Application):

	def __init__(self):
		super().__init__()

		# Banner
		print("BitSwan BSPump version {}".format(__version__))

		from asab.metrics import Module
		self.add_module(Module)

		#TODO: Make sure that we don't occupy unnecessary high amount of threads
		from asab.proactor import Module
		self.add_module(Module)

		self.PumpService = BSPumpService(self)
		self.WebService = None

		# Conditionally activate LogMan.io service
		if asab.Config.has_section("logman.io"):
			from asab.logman import Module
			self.add_module(Module)
			logman_service = self.get_service('asab.LogManIOService')
			logman_service.configure_metrics(self.get_service('asab.MetricsService'))
			logman_service.configure_logging(self)


		try:
			# Signals are not available on Windows
			self.Loop.add_signal_handler(signal.SIGUSR1, self._on_signal_usr1)
		except (NotImplementedError, AttributeError):
			pass


	def create_argument_parser(self):
		prog = sys.argv[0]
		if prog[-11:] == '__main__.py':
			prog = sys.executable + " -m bspump"

		description = '''
BSPump is a stream processor. It is a part of BitSwan.
For more information, visit: https://github.com/TeskaLabs/bspump

version: {}
build: {} [{}]
'''.format(__version__, __build__, __build__[:7])


		parser = super().create_argument_parser(
			prog=prog,
			description=description
		)
		parser.add_argument(
			'-w', '--web',
			const="0.0.0.0 80",
			nargs="?",
			metavar="ADDRESS",
			help='Enable the web API, ADDRESS specify an listen address such as "0.0.0.0 80"'
		)
		return parser


	def parse_arguments(self):
		args = super().parse_arguments()
		self._web_listen = args.web


	async def initialize(self):
		# Conditionally activate also a web service
		if not asab.Config.has_section("bspump:web"):
			asab.Config["bspump:web"] = {}

		# Listen host and port
		listen = ""
		if self._web_listen is not None and len(self._web_listen) > 0:
			listen = self._web_listen
		else:
			listen = asab.Config["bspump:web"].get("listen", "")

		if len(listen) > 0:
			from .web import initialize_web
			self.WebService = initialize_web(self, listen)


	async def main(self):
		print("{} pipeline(s) ready.".format(len(self.PumpService.Pipelines)))


	def _on_signal_usr1(self):
		'''
		To clear reset from all pipelines, run 
		$ kill -SIGUSR1 xxxx
		Equivalently, you can use `docker kill -s SIGUSR1 ....` to reset containerized BSPump.
		'''
		# Reset errors from all pipelines
		for pipeline in self.PumpService.Pipelines.values():
			if not pipeline.is_error(): continue # Focus only on pipelines that has errors
			pipeline.set_error(None, None, None)

