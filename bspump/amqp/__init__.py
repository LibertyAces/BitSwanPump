import asab
from .driver import AMQPDriver
from .source import AMQPSource

asab.Config.add_defaults(
	{
		'amqp' : {
			'url': 'amqp://localhost/',
			'queue': 'i.q',
			'error_exchange': 'error',
			'appname': 'bspump.py', # For a AMQP client properties
			'prefetch_count': '5000',
			'reconnect_delay': 10.0,
		},
	}
)
