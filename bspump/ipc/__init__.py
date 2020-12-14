# IPC = InterProcess Communication

from .datagram import DatagramSource, DatagramSink

from .stream_client_sink import StreamClientSink
from .stream_server_source import StreamServerSource

# Backward compatibility
StreamSource = StreamServerSource
StreamSink = StreamClientSink

__all__ = (
	'DatagramSource',
	'DatagramSink',
	'StreamServerSource',
	'StreamClientSink',
	'StreamSink',
	'StreamSource',
)
