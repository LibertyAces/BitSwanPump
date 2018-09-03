BSPump: A real-time stream processor for Python 3.5+
====================================================

.. image:: https://badges.gitter.im/TeskaLabs/bspump.svg
    :alt: Join the chat at https://gitter.im/TeskaLabs/bspump
    :target: https://gitter.im/TeskaLabs/bspump?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge

Principles
----------

* Write once, use many times
* Schema-less
* High performance
* Back pressure
* Simple to use and well documented, so anyone can write their own stream processor
* Sliding time window
* Asynchronous via Python 3.5+ ``async``/``await`` and ``asyncio``
* `Event driven Architecture <https://en.wikipedia.org/wiki/Event-driven_architecture>`_ / `Reactor pattern <https://en.wikipedia.org/wiki/Reactor_pattern>`_
* Single-threaded core but compatible with threads
* Compatible with `pypy <http://pypy.org>`_, Just-In-Time compiler capable of boosting Python code performace more then 5x times
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



High-level architecture
-----------------------


.. image:: ./doc/_static/bspump-architecture.png
    :alt: Schema of BSPump high-level achitecture


Licence
-------

BSPump is an open-source software, available under BSD 3-Clause License.
BSPump is a part of Black Swan project, joint effort of Liberty Aces and TeskaLabs.
