import asyncio
import logging
import socket

from ..abc.sink import Sink

from .stream import Stream, TLSStream

#

L = logging.getLogger(__name__)

#


class StreamClientSink(Sink):

	ConfigDefaults = {
		'address': '127.0.0.1 8888',  # IPv4, IPv6 or unix socket path
	}


	def __init__(self, app, pipeline, id=None, config=None):
		super().__init__(app, pipeline, id=id, config=config)
		self.OutboundQueue = asyncio.Queue()

		# Throttle till we are connected
		self.Pipeline.throttle(self, enable=True)

		self.Task = None

		self.Pipeline.PubSub.subscribe("bspump.pipeline.start!", self._open_connection)
		self.Pipeline.PubSub.subscribe("bspump.pipeline.stop!", self._close_connection)


	async def _open_connection(self, message, pipeline):
		loop = self.Pipeline.Loop

		addr = self.Config['address']
		host, port = addr.rsplit(" ", maxsplit=1)
		addrinfo = await loop.getaddrinfo(host, port, family=socket.AF_UNSPEC, type=socket.SOCK_STREAM)

		s = None
		connection_exception = ''
		for family, socktype, proto, canonname, sockaddr in addrinfo:
			s = socket.socket(family, socktype, proto)
			s.setblocking(False)
			try:
				await loop.sock_connect(s, sockaddr)
			except Exception as e:
				connection_exception = e
				s = None
				continue

		if s is None:
			L.warning("Connection to '{}' failed: {}".format(addr, connection_exception))
			return

		# Connection is established
		if self.Task is not None:
			L.warning("There is existing task")
			self.Task.cancel()

		self.Task = loop.create_task(
			self._client_connected_task(s)
		)

		# Untrottle
		self.Pipeline.throttle(self, enable=False)


	async def _close_connection(self, message, pipeline):

		# Trottle
		self.Pipeline.throttle(self, enable=True)

		if self.Task is not None:
			self.Task.cancel()
			self.Task = None


	async def _client_connected_task(self, client_sock):
		# TODO: Support also TLSStream ...
		stream = Stream(self.Pipeline.Loop, client_sock, outbound_queue=self.OutboundQueue)

		outbound = stream.outbound()
		inbound = self._client_inbound_task(client_sock)
		done, active = await asyncio.wait(
			{outbound, inbound},
			return_when=asyncio.FIRST_COMPLETED
		)

		self.Pipeline.throttle(self, enable=True)

		for t in active:
			# TODO: There could be outstanding data in the outbound queue
			#       Consider flushing them
			# Cancel remaining active tasks
			t.cancel()

		for t in done:
			try:
				await t
			except asyncio.CancelledError:
				pass
			except Exception:
				L.exception("Error when handling client socket")

		# Close the stream
		await stream.close()


	async def _client_inbound_task(self, client_sock):
		'''
		This is the monitor of the client connection.
		'''
		while True:
			data = await self.Pipeline.Loop.sock_recv(client_sock, 4096)
			if len(data) == 0:
				# Client closed the connection
				return

			# Incoming data are discarted ...


	def process(self, context, event):
		self.OutboundQueue.put_nowait(event)
		# TODO: Throttle the pipeline if the queue is full
