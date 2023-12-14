import codecs


class SourceProtocolABC(object):
	'''
	Source protocol is a handler class, that basically gets the socket (in reader)
	and extract the payload from it in a way that is conformant to expected protocol.

	That is happening in the `handle()` method.
	The output is to be shipped to source.process() method.
	'''

	def __init__(self, app, pipeline, config):
		self.Loop = app.Loop
		self.Pipeline = pipeline

	async def handle(self, source, stream, context):
		'''
		`source` is an Source object, call `process()` method with the output of the protocol
		`stream` is an incoming Stream
		`context` is a dictionary with context info.


		Example of the naive protocol output:

		```
			buffer = bytearray(b' ' * 1024 * 8)
			await stream.recv_into(buffer)
			await source.process(buffer, context=context.copy())
		```

		'''
		raise NotImplementedError()


	async def process(self, source, event, context):
		await self.Pipeline.ready()
		await source.process(event, context=context.copy())



class LineSourceProtocol(SourceProtocolABC):
	'''
	Description: Basically readline() for reading lines from a socket.
	'''

	def __init__(self, app, pipeline, config):
		super().__init__(app, pipeline, config)

		# TODO: All following values could be read from configuration
		self.EOL = b'\n'
		self.ChunkSize = 1024

		# Line decoder
		decode_codec = config['decode']
		if decode_codec == "bytes":
			self.Codec = None
			self.LineDecoder = self._line_bytes_decoder
		else:
			self.Codec = codecs.lookup(decode_codec)
			self.LineDecoder = self._line_codec_decoder


	async def handle(self, source, stream, context):

		# Create an empty bytearray to store the received data
		buffer = bytearray()

		while True:
			# Read data from the stream
			chunk = await stream.recv(self.ChunkSize)
			if not chunk:
				# If no more data, break the loop
				break

			buffer.extend(chunk)

			# Check if there are any newline characters in the buffer
			while True:
				# Split the buffer at the first newline character
				try:
					line, buffer = buffer.split(self.EOL, 1)
				except ValueError:
					break

				line = self.LineDecoder(line)
				await self.process(source, line, context)
		
		# Process any remaining data in the buffer if it's not empty
		if buffer:
			line = self.LineDecoder(buffer)
			await self.process(source, line, context)


	def _line_codec_decoder(self, line_bytes):
		line, _ = self.Codec.decode(
			line_bytes
		)
		return line

	def _line_bytes_decoder(self, line_bytes):
		return line_bytes
