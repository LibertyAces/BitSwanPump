IPC
===

Datagram
--------

.. py:currentmodule:: bspump.ipc.datagram

.. autoclass:: DatagramSource
    :show-inheritance:

.. automethod:: bspump.ipc.datagram.DatagramSource.__init__()

.. automethod:: bspump.ipc.datagram.DatagramSource.main


Datagramsink
~~~~~~~~~~~~

.. py:currentmodule:: bspump.ipc.datagram

.. autoclass:: DatagramSink
    :show-inheritance:

.. automethod:: bspump.ipc.datagram.DatagramSink.__init__()

.. automethod:: bspump.ipc.datagram.DatagramSink.process


Protocol
--------

.. py:currentmodule:: bspump.ipc.protocol

.. autoclass:: SourceProtocolABC
    :show-inheritance:

.. automethod:: bspump.ipc.protocol.SourceProtocolABC.__init__()

.. automethod:: bspump.ipc.protocol.SourceProtocolABC.handle


Line Source Protocol
~~~~~~~~~~~~~~~~~~~~

.. py:currentmodule:: bspump.ipc.protocol

.. autoclass:: LineSourceProtocol
    :show-inheritance:

.. automethod:: bspump.ipc.protocol.LineSourceProtocol.__init__()

.. automethod:: bspump.ipc.protocol.LineSourceProtocol.handle


Stream
------

.. py:currentmodule:: bspump.ipc.stream

.. autoclass:: Stream
    :show-inheritance:

.. automethod:: bspump.ipc.stream.Stream.__init__()

.. automethod:: bspump.ipc.stream.Stream.recv_into

.. automethod:: bspump.ipc.stream.Stream.send

.. automethod:: bspump.ipc.stream.Stream.outbound

.. automethod:: bspump.ipc.stream.Stream.close


TLS Stream
~~~~~~~~~~

.. py:currentmodule:: bspump.ipc.stream

.. autoclass:: TLSStream
    :show-inheritance:

.. automethod:: bspump.ipc.stream.TLSStream.__init__()

.. automethod:: bspump.ipc.stream.TLSStream.recv_into

.. automethod:: bspump.ipc.stream.TLSStream.send

.. automethod:: bspump.ipc.stream.TLSStream.outbound

.. automethod:: bspump.ipc.stream.TLSStream.close


Steam Server Source
-------------------

.. py:currentmodule:: bspump.ipc.stream_server_source

.. autoclass:: StreamServerSource
    :show-inheritance:

.. automethod:: bspump.ipc.stream_server_source.StreamServerSource.__init__()

.. automethod:: bspump.ipc.stream_server_source.StreamServerSource.start

.. automethod:: bspump.ipc.stream_server_source.StreamServerSource.stop

.. automethod:: bspump.ipc.stream_server_source.StreamServerSource.main


Stream Client Sink
------------------

.. py:currentmodule:: bspump.ipc.stream_client_sink

.. autoclass:: StreamClientSink
    :show-inheritance:

.. automethod:: bspump.ipc.stream_client_sink.StreamClientSink.__init__()

.. automethod:: bspump.ipc.stream_client_sink.StreamClientSink.process
