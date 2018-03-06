import logging
import asab
from .driver import AMQPDriver


L = logging.getLogger(__name__)

#

asab.Config.add_defaults(
	{
		'amqp' : {
			'uri': 'amqp://localhost/',
			'queue': 'i.q',
			'error_exchange': 'error',
			'appname': 'bspump.py', # For a AMQP client properties
			'prefetch': '5000',
		},
	}
)


class AMQPService(asab.Service):

	def __init__(self):
		self.drivers = {}

	def create_driver(self, id, conf=None):
		d

class AMQPModule(asab.Module):

	def __init__(self, app):
		super().__init__(app)

		_amqp_service = AMQPService(app)
		app.register_service("amqp", _amqp_service)

		L.info("AMQP module loaded.")
