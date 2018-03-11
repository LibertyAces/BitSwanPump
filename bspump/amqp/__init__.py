import asab
from .connection import AMQPConnection
from .source import AMQPSource
from .sink import AMQPSink

asab.Config.add_defaults(
	{
		'amqp' : {
			'queue': 'teskalabs.q',
			'error_exchange': 'error',
			'prefetch_count': '5000',
		},
	}
)
