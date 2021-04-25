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

	async def handle(self, source, stream, context):
		raise NotImplementedError()


class LineSourceProtocol(SourceProtocolABC):
	'''
	Basically readline() for reading lines from a socket.
	'''

	def __init__(self, app, pipeline, config):
		super().__init__(app, pipeline, config)

		# TODO: All following values could be read from configuration
		self.EOL = b'\n'
		self.Codec = codecs.lookup('utf-8')
		self.SaneBufferSize = 64 * 1024  # The maximum buffer size considered as sane


	async def handle(self, source, stream, context):
		pipeline = source.Pipeline

		input_buffer = bytearray(b' ' * 8)
		input_buffer_mv = memoryview(input_buffer)
		input_buffer_pos = 0
		last_eol_pos = 0

		while True:
			recv_bytes = await stream.recv_into(input_buffer_mv[input_buffer_pos:])
			if recv_bytes <= 0:
				# Client closed the connection
				if recv_bytes < 0:
					raise RuntimeError("Client sock_recv_into returned {}".format(recv_bytes))
				return

			input_buffer_pos += recv_bytes
			if len(input_buffer) == input_buffer_pos:
				if len(input_buffer) > self.SaneBufferSize:
					raise RuntimeError("Insane buffer size requested")
				# Grow the input_buffer if the size touches the top
				new_input_buffer = bytearray(b' ' * (len(input_buffer) * 2))
				input_buffer_mv = memoryview(new_input_buffer)
				input_buffer_mv[:len(input_buffer)] = input_buffer  # Copy the content of the old buffer
				input_buffer = new_input_buffer

			while last_eol_pos < input_buffer_pos:
				# Seek for end of line symbol in the buffer
				eol_pos = input_buffer[:input_buffer_pos].find(self.EOL, last_eol_pos)
				if eol_pos == -1:
					break

				line, _ = self.Codec.decode(
					input_buffer[last_eol_pos:eol_pos]
				)
				last_eol_pos = eol_pos + 1

				await pipeline.ready()
				await source.process(line, context=context.copy())

			# If the '\n' is at the end of the buffer, reset the buffer position
			if last_eol_pos == input_buffer_pos:
				input_buffer_pos = 0
				last_eol_pos = 0
				continue
