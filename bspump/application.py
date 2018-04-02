import asab

from .service import BSPumpService

class BSPumpApplication(asab.Application):

	def __init__(self):
		super().__init__()

		self.PumpService = BSPumpService(self)


	async def main(self):
		self.PumpService.start()
