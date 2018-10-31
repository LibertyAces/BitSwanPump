import signal

import asab

from .service import BSPumpService


class BSPumpApplication(asab.Application):


	def __init__(self):
		super().__init__()

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
		parser = super().create_argument_parser()
		parser.add_argument(
			'-w', '--web',
			default="",
			const="0.0.0.0 80",
			nargs="?")
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
		if len(self._web_listen) > 0:
			listen = self._web_listen
		else:
			listen = asab.Config["bspump:web"].get("listen", "")

		if len(listen) > 0:
			from .web import initialize_web
			self.WebService = initialize_web(self, listen)


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

