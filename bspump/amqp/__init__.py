import asab
from .connection import AMQPConnection
from .source import AMQPSource
from .sink import AMQPSink

asab.Config.add_defaults(
	{
		'amqp' : {
			'url': 'amqp://localhost/',
			'queue': 'teskalabs.q',
			'error_exchange': 'error',
			'appname': 'bspump.py', # For a AMQP client properties
			'prefetch_count': '5000',
			'reconnect_delay': 10.0,
		},
	}
)
