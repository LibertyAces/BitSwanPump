import asab

from .service import BSPumpService

class BSPumpApplication(asab.Application):

	def __init__(self, web=False):
		super().__init__()

		self.PumpService = BSPumpService(self)

		# Conditionally activate also a web service
		if web:
			from .web import initialize_web
			self.WebService = initialize_web(self)
		else:
			self.WebService = None


	async def main(self):
		self.PumpService.start()
