import asab

from .service import BSPumpService

class BSPumpApplication(asab.Application):

	def __init__(self):
		super().__init__()

		self.PumpService = BSPumpService(self)
		self.register_service("bspump.PumpService", self.PumpService)

	async def main(self):
		await self.PumpService.main()
