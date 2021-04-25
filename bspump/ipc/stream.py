import logging
import ssl

#

L = logging.getLogger(__name__)

#


class Stream(object):
	'''
	This object represent a client connection.
	It is unencrypted STREAM socket.
	'''

	def __init__(self, loop, socket):
		self.Loop = loop
		self.Socket = socket


	async def recv_into(self, buf):
		return await self.Loop.sock_recv_into(self.Socket, buf)

	def send(self, data):
		# Handle WOULDBLOCK situations ...
		self.Socket.send(data)

	async def close(self):
		self.Socket.close()


class TLSStream(object):
	'''
	This object represent a TLS client connection.
	It is encrypted SSL/TLS socket abstraction.
	'''

	def __init__(self, loop, sslcontext, socket, server_side: bool):
		self.Loop = loop
		self.Socket = socket

		self.SSLContext = sslcontext

		self.InBuffer = ssl.MemoryBIO()
		self.OutBuffer = ssl.MemoryBIO()

		self.SSLSocket = sslcontext.wrap_bio(self.InBuffer, self.OutBuffer, server_side=server_side)


	async def handshake(self):
		while True:

			try:
				self.SSLSocket.do_handshake()
				break

			except ssl.SSLWantReadError:

				if self.OutBuffer.pending > 0:
					data = self.OutBuffer.read()
					await self.Loop.sock_sendall(self.Socket, data)

				data = await self.Loop.sock_recv(self.Socket, 4096)
				if len(data) == 0:
					# Socket has been closed
					# TODO: self.Socket.shutdown()
					return False

				self.InBuffer.write(data)
				continue

			except Exception:
				L.exception("SSL handshake failed")
				self.Socket.close()
				return False

		# Flush output buffer to complete the handshake on the client side as well
		if self.OutBuffer.pending > 0:
			data = self.OutBuffer.read()
			await self.Loop.sock_sendall(self.Socket, data)

		return True


	async def recv_into(self, buf):
		while True:

			try:
				data = self.SSLSocket.read(len(buf))
				if len(data) == 0:
					# Socket has been closed
					return 0

				buf[:len(data)] = data
				return len(data)

			except ssl.SSLWantReadError:

				if self.OutBuffer.pending > 0:
					data = self.OutBuffer.read()
					await self.Loop.sock_sendall(self.Socket, data)

				data = await self.Loop.sock_recv(self.Socket, 4096)
				if len(data) == 0:
					# Socket has been closed
					# TODO: self.Socket.shutdown()
					return 0

				self.InBuffer.write(data)
				continue


	def send(self, data):
		self.SSLSocket.write(data)
		# Handle WOULDBLOCK situations ...


	async def close(self):
		self.Socket.close()
