import asyncio
import logging
import ssl

import asab

#

L = logging.getLogger(__name__)

#


class Stream(object):
	'''
	Description: This object represent a client connection.
	It is unencrypted STREAM socket.
	'''

	def __init__(self, loop, socket, outbound_queue=None):
		self.Loop = loop
		self.Socket = socket
		if outbound_queue is None:
			self.OutboundQueue = asyncio.Queue()
		else:
			self.OutboundQueue = outbound_queue


	async def recv_into(self, buf):
		return await self.Loop.sock_recv_into(self.Socket, buf)

	async def recv(self, nbytes):
		return await self.Loop.sock_recv(self.Socket, nbytes)


	def send(self, data):
		self.OutboundQueue.put_nowait(data)


	async def outbound(self):
		'''
		Handle outbound direction
		'''
		while True:

			try:
				data = await self.OutboundQueue.get()

			except RuntimeError as e:
				# Event loop has been closed during .get() call likely b/c of the application exit
				L.warning("Outbound queue for Stream has been closed: '{}'.".format(e))
				break

			if data is None:
				break

			await self.Loop.sock_sendall(self.Socket, data)


	async def close(self):
		self.Socket.close()


class TLSStream(object):
	'''
	Description: This object represent a TLS client connection.
	It is encrypted SSL/TLS socket abstraction.
	'''

	def __init__(self, loop, sslcontext, socket, server_side: bool):
		self.Loop = loop
		self.Socket = socket

		self.SSLContext = sslcontext

		self.InBuffer = ssl.MemoryBIO()
		self.OutBuffer = ssl.MemoryBIO()
		self.OutboundQueue = asyncio.Queue()

		self.SSLSocket = sslcontext.wrap_bio(self.InBuffer, self.OutBuffer, server_side=server_side)


	async def handshake(self):
		"""
		Description:

		:return: False if error is raised or socket is closed, otherwise returns True.

		|

		"""
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
		self.OutboundQueue.put_nowait(data)


	async def outbound(self):
		'''
		Handle outbound direction
		'''
		while True:

			try:
				data = await self.OutboundQueue.get()

			except RuntimeError as e:
				# Event loop has been closed during .get() call likely b/c of the application exit
				L.warning("Outbound queue for Stream has been closed: '{}'.".format(e))
				break

			if data is None:
				break

			self.SSLSocket.write(data)

			while self.OutBuffer.pending > 0:
				data = self.OutBuffer.read()
				await self.Loop.sock_sendall(self.Socket, data)


	async def close(self):
		self.OutboundQueue.put_nowait(None)
		self.Socket.close()
