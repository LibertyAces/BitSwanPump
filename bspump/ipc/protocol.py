import abc


class SourceProtocolABC(abc.ABC):
	'''
	Source protocol is a handler class, that basically gets the socket (in reader)
	and extract the payload from it in a way that is conformant to expected protocol.

	That is happening in the `handle()` method.
	The output is to be shipped to source.process() method.
	'''

	def __init__(self, source, app, pipeline, config):
		pass

	@abc.abstractmethod
	async def inbound(self, source, reader, context):
		pass


class LineSourceProtocol(SourceProtocolABC):
	'''
	Basically readline() construct for reading lines from a socket.
	'''

	async def inbound(self, source, reader, context):
		pipeline = source.Pipeline
		while True:
			await pipeline.ready()
			data = await reader.readline()

			# End of stream detected
			if len(data) == 0:
				break

			await source.process(data, context=context.copy())
			print("Cycled")