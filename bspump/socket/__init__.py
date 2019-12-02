from ..ipc import DatagramSource, StreamSource

# Backward compatibility
from ..ipc import DatagramSource as UDPSource
from ..ipc import StreamSource as TCPSource
from ..ipc import StreamSource as TCPStreamSource


__all__ = [
	"DatagramSource",
	"StreamSource",
	"UDPSource",
	"TCPSource",
	"TCPStreamSource",
]
