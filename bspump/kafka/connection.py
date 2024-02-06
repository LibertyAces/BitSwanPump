import logging

import asab

from ..abc.connection import Connection

#

L = logging.getLogger(__name__)

#


class KafkaConnection(Connection):
	"""
	KafkaConnection serves to connect BSPump application with an instance of Apache Kafka messaging system.
	It can later be used by processors to consume or provide user-defined messages.

.. code:: python

	config = {"bootstrap_servers": "localhost:9092"}
	app = bspump.BSPumpApplication()
	svc = app.get_service("bspump.PumpService")
	svc.add_connection(
		bspump.kafka.KafkaConnection(app, "KafkaConnection", config)
	)

	Standard Kafka configuration options can be used,
	as specified in librdkafka library,
	where the options are simply passed to:

	https://github.com/edenhill/librdkafka/blob/master/CONFIGURATION.md
	"""

	ConfigDefaults = {
	}

	def __init__(self, app, id=None, config=None):
		super().__init__(app, id=id, config=config)

		if self.Config.get("bootstrap_servers") is None:
			if "kafka" in asab.Config:
				self.Config.update(asab.Config["kafka"])

		if self.Config.get("bootstrap_servers") is None:
			raise RuntimeError("Missing 'bootstrap_servers' in Kafka connection configuration.")
