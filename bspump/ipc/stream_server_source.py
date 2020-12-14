import socket
import asyncio
import logging

from ..abc.source import Source

from .protocol import LineSourceProtocol

#

L = logging.getLogger(__name__)

#


class StreamServerSource(Source):

	ConfigDefaults = {
		'address': '127.0.0.1:8888',  # IPv4, IPv6 or unix socket path
		# Specify 'cert' or 'key' to enable SSL / TLS mode
	}

	def __init__(self, app, pipeline, id=None, config=None):
		super().__init__(app, pipeline, id=id, config=config)

		self.Writers = set()

		self.Address = str(self.Config['address'])

		if 'cert' in self.Config or 'key' in self.Config:
			import ssl
			import asab.net
			sslbuilder = asab.net.SSLContextBuilder('[none]', config=self.Config)
			self.SSL = sslbuilder.build(protocol=ssl.PROTOCOL_TLS_SERVER)
		else:
			self.SSL = None

		# TODO: Allow to specify other protocols such as BlockSourceProtocol, BytesSourceProtocol
		self.Protocol = LineSourceProtocol(self, app, pipeline, config)


	async def _on_connection(self, reader, writer):

		# Prepare the context
		sock = writer.transport.get_extra_info('socket')

		# Peer
		peer_name = writer.transport.get_extra_info('peername')
		sock_name = writer.transport.get_extra_info('sockname')
		if sock.family is socket.AF_INET:
			me = '{}:{}'.format(sock_name[0], sock_name[1])
			peer = '{}:{}'.format(peer_name[0], peer_name[1])
		elif sock.family is socket.AF_INET6:
			me = '[{}]:{}'.format(sock_name[0], sock_name[1])
			peer = '[{}]:{}'.format(peer_name[0], peer_name[1])
		else:
			me = sock_name
			peer = peer_name

		context = {
			'stream_type': sock.family.name,
			'stream_dir': 'in',
			'stream_peer': peer,
			'stream_me': me
		}

		self.Writers.add(writer)

		try:
			await self.Protocol.inbound(self, reader, context)

		finally:
			writer.close()
			self.Writers.remove(writer)


	async def main(self):
		# Start server
		if ":" in self.Address:
			host, port = self.Address.rsplit(":", maxsplit=1)
			(family, socktype, proto, canonname, sockaddr) = socket.getaddrinfo(host, port)[0]
			host, port = sockaddr
			server = await asyncio.start_server(
				self._on_connection,
				host, port,
				loop=self.Pipeline.App.Loop,
				ssl=self.SSL,
			)
		else:
			server = await asyncio.start_unix_server(
				self._on_connection,
				path=self.Address,
				loop=self.Pipeline.App.Loop,
				ssl=self.SSL,
			)

		await self.stopped()

		# Close server
		server.close()
		await server.wait_closed()

		# Close peer connections
		for writer in self.Writers:
			L.warning("'{}' closes connection to '{}'".format(
				self.Id,
				writer.transport.get_extra_info('peername'))
			)
			if writer.can_write_eof():
				writer.write_eof()
			writer.close()
