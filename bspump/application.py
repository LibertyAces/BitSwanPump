import asab

from .service import BSPumpService


class BSPumpApplication(asab.Application):

	def __init__(self):
		super().__init__()

		from asab.metrics import Module
		self.add_module(Module)

		self.PumpService = BSPumpService(self)

		# Conditionally activate also a web service
		if asab.Config.has_section("asab:web"):
			listen = asab.Config["asab:web"].get("listen", "")
			if len(listen) > 0:
				# Initialize web service
				from .web import initialize_web
				self.WebService = initialize_web(self)

		else:
			self.WebService = None


	async def main(self):
		self.PumpService.start()
