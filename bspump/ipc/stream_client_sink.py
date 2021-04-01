import asyncio
import logging
import socket
import types

from ..abc.sink import Sink

#

L = logging.getLogger(__name__)

#


class StreamClientSink(Sink):

	ConfigDefaults = {
		'address': '127.0.0.1:8888',  # IPv4, IPv6 or unix socket path
	}

	def __init__(self, app, pipeline, id=None, config=None):
		super().__init__(app, pipeline, id=id, config=config)

		self.LastEvent = None
		self.Writer = self.Reader = None
		self.Pipeline.throttle(self, enable=True)

		self.Address = str(self.Config['address'])
		self.Pipeline.PubSub.subscribe("bspump.pipeline.start!", self._open_connection)
		self.Pipeline.PubSub.subscribe("bspump.pipeline.stop!", self._close_connection)
		app.PubSub.subscribe("Application.tick!", self._health_check)


	async def _open_connection(self, message, pipeline):
		assert self.Writer is None
		if ":" in self.Address:
			host, port = self.Address.rsplit(":", maxsplit=1)
			(family, socktype, proto, canonname, sockaddr) = socket.getaddrinfo(host, port)[0]
			host, port = sockaddr
			self.Reader, self.Writer = await asyncio.open_connection(host, port)
		else:
			self.Reader, self.Writer = await asyncio.open_unix_connection(self.Address)

		# Manual adding of asyncio fix to asyncio.transport._SelectorSocketTransport
		self.Writer.transport.write = types.MethodType(write, self.Writer.transport)

		if self.LastEvent is not None:
			try:
				self.Writer.write(self.LastEvent)
				self.LastEvent = None
			except Exception as e:
				L.error("Exception occurred while sending last event in open connection '{}'.".format(e))

		pipeline.throttle(self, enable=False)


	async def _close_connection(self, message, pipeline):

		if self.Reader:
			self.Reader = None
		if self.Writer:
			self.Writer.close()
			self.Writer = None
			pipeline.throttle(self, enable=True)

		assert not self.Writer


	async def _health_check(self, message):
		if self.Reader:
			if self.Reader.at_eof():
				L.warning("Connection lost. Closing StreamClientSink.")
				await self._close_connection(message, self.Pipeline)

		if self.Writer is None:
			# Hotfix: Make sure the connection is always closed before reopening,
			# so asyncio does not remember the previous socket descriptor
			await self._close_connection(message, self.Pipeline)
			await self._open_connection(message, self.Pipeline)

	def process(self, context, event):
		try:
			self.Writer.write(event)

		except RuntimeError as e:
			# Hotfix for: RuntimeError: File descriptor 7 is used by transport
			L.error("During sending event, the following RuntimeError occurred: '{}'.".format(e))
			self.LastEvent = event

			# Health check will recreate the connection
			if self.Writer is not None:
				self.Writer.close()
				self.Writer = None
			if self.Reader is not None:
				self.Reader = None


# Custom implementation of write method of private class asyncio.transport._SelectorSocketTransport
def write(self, data):
	if not isinstance(data, (bytes, bytearray, memoryview)):
		raise TypeError('data argument must be byte-ish (%r)',
						type(data))
	if self._eof:
		raise RuntimeError('Cannot call write() after write_eof()')
	if not data:
		return

	if self._conn_lost:
		if self._conn_lost >= asyncio.constants.LOG_THRESHOLD_FOR_CONNLOST_WRITES:
			# Custom implementation starts
			# Instead of printing the warning, end the connection with fatal error
			# Requires implementation of custom health check of the connection
			self._fatal_error(
				RuntimeError("Log threshold for connection lost writes exceeded."),
				'Fatal error when writing in socket.send().'
			)
			# Custom implementation ends
		self._conn_lost += 1
		return

	if not self._buffer:
		# Optimization: try to send now.
		try:
			n = self._sock.send(data)
		except (BlockingIOError, InterruptedError):
			pass
		except Exception as exc:
			self._fatal_error(exc, 'Fatal write error on socket transport')
			return
		else:
			data = data[n:]
			if not data:
				return
		# Not all was written; register write handler.
		self._loop.add_writer(self._sock_fd, self._write_ready)

	# Add it to the buffer.
	self._buffer.extend(data)
	self._maybe_pause_protocol()
