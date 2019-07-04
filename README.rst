BSPump: A real-time stream processor for Python 3.5+
====================================================

.. image:: https://badges.gitter.im/TeskaLabs/bspump.svg
    :alt: Join the chat at https://gitter.im/TeskaLabs/bspump
    :target: https://gitter.im/TeskaLabs/bspump?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge

Principles
----------

* Write once, use many times
* Everything is a stream
* Schema-less
* Kappa architecture
* Real-Time
* High performance
* Simple to use and well documented, so anyone can write their own stream processor
* Asynchronous via Python 3.5+ ``async``/``await`` and ``asyncio``
* `Event driven Architecture <https://en.wikipedia.org/wiki/Event-driven_architecture>`_ / `Reactor pattern <https://en.wikipedia.org/wiki/Reactor_pattern>`_
* Single-threaded core but compatible with threads
* Compatible with `pypy <http://pypy.org>`_, Just-In-Time compiler capable of boosting Python code performace more then 5x times
* Good citizen of the Python ecosystem 
* Modularized


Stream processor example
------------------------


.. code:: python

    #!/usr/bin/env python3
    import bspump
    import bspump.socket
    import bspump.common
    import bspump.elasticsearch
    
    class MyPipeline(bspump.Pipeline):
        def __init__(self, app):
            super().__init__(app)
            self.build(
                bspump.socket.TCPStreamSource(app, self),
                bspump.common.JSONParserProcessor(app, self),
                bspump.elasticsearch.ElasticSearchSink(app, self, "ESConnection")
            )
    
    
    if __name__ == '__main__':
        app = bspump.BSPumpApplication()
        svc = app.get_service("bspump.PumpService")
        svc.add_connection(bspump.elasticsearch.ElasticSearchConnection(app, "ESConnection"))
        svc.add_pipeline(MyPipeline(app))
        app.run()

Video tutorial
^^^^^^^^^^^^^^

.. image:: http://img.youtube.com/vi/QvjiPxO4w6w/0.jpg
   :target: https://www.youtube.com/watch?v=QvjiPxO4w6w&list=PLb0LvCJCZKt_1QcQwpJXqsm-AY_ty4udo

Blank application setup
-----------------------
You can clone blank application from `it's own repository <https://github.com/LibertyAces/BitSwanTelco-BlankApp>`_.


Available technologies
----------------------

* ``bspump.amqp`` AMQP/RabbitMQ connection, source and sink
* ``bspump.elasticsearch`` ElasticSearch connection, source and sink
* ``bspump.file`` (plain files, JSON, CSV)
* ``bspump.http.client``  HTTP client source, WebSocket client sink
* ``bspump.http.web`` HTTP server source and sink, WebSocket server source
* ``bspump.influxdb`` InfluxDB connection and sink
* ``bspump.kafka`` Kafka connection, source and sink
* ``bspump.mysql`` MySQL connection, source and sink
* ``bspump.postgresql`` PostgreSQL connection and sink
* ``bspump.parquet`` Apache Parquet file sink
* ``bspump.avro`` Apache Avro file source and sink
* ``bspump.socket`` TCP source, UDP source
* ``bspump.mongodb`` MongoDB connection and lookup
* ``bspump.slack`` Slack connection and sink
* ``bspump.trigger`` Opportunistic, PubSub and Periodic triggers
* ``bspump.mail`` SMTP connection and sink
* ``bspump.crypto`` Cryptography

  * Hashing: SHA224, SHA256, SHA384, SHA512, SHA1, MD5, BLAKE2b, BLAKE2s
  * Symmetric Encryption: AES 128, AES 192, AES 256

* ``bspump.analyzer``

  * Time Window analyzer
  * Session analyzer
  * Geographical analyzer
  * Time Drift analyzer

* ``bspump.lookup``

  * GeoIP Lookup

* ``bspump.unittest``

  * Interface for testing Processors / Pipelines

Google Sheet with technological compatiblity matrix:
https://docs.google.com/spreadsheets/d/1L1DvSuHuhKUyZ3FEFxqEKNpSoamPH2Z1ZaFuHyageoI/edit?usp=sharing


High-level architecture
-----------------------


.. image:: ./doc/_static/bspump-architecture.png
    :alt: Schema of BSPump high-level achitecture


Unit test
---------

.. code:: python

    from bspump.unittest import ProcessorTestCase
    from unittest.mock import MagicMock

    import bspump.unittest

    class MyProcessorTestCase(ProcessorTestCase)

        def test_my_processor(self):

            # setup processor for test
            self.set_up_processor(my_project.processor.MyProcessor)

            # mock methods to suit your needs on pipieline ..
            self.Pipeline.method = MagicMock()

            # .. or instance of processor
            my_processor = self.Pipeline.locate_processor("MyProcessor")
            my_processor.method = MagicMock()

            output = self.execute(
                [(None, {'foo': 'bar'})]  # Context, event
            )

            # assert output
            self.assertEqual(
                [event for context, event in output],
                [{'FOO': 'BAR'}]
            )

            # asssert expected calls on `self.Pipeline.method` or `my_processor.method`
            my_processor.method.assert_called_with(**expected)


Runnig tests
------------
`python3 -m unittest path_to_my_test`


Licence
-------

BSPump is an open-source software, available under BSD 3-Clause License.

