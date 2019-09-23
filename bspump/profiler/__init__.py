import asab
from .service import ProfilerService


class Module(asab.Module):

	def __init__(self, app):
		super().__init__(app)
		self.service = ProfilerService(app, "bspump.ProfilerService")
