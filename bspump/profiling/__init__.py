import asab
from .service import ProfilingService


class Module(asab.Module):

	def __init__(self, app):
		super().__init__(app)
		self.service = ProfilingService(app, "bspump.ProfilingService")
