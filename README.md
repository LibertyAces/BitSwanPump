# BSPump: A real-time stream processor for Python 3.5+

[![Join the chat at https://gitter.im/TeskaLabs/bspump](https://badges.gitter.im/TeskaLabs/bspump.svg)](https://gitter.im/TeskaLabs/bspump?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)

## Principles

 * Write once, use many times
 * Schema-less
 * Orthogonal
 * High performance
 * Simple to use and well documented, so anyone can write their own stream processor
 * Sliding time window
 * Asynchronous via Python 3.5+ `async`/`await` and `asyncio`
 * [Event-driven Architecture](https://en.wikipedia.org/wiki/Event-driven_architecture) / [Reactor pattern](https://en.wikipedia.org/wiki/Reactor_pattern)
 * Single-threaded core but compatible with threads
 * Compatible with [pypy](http://pypy.org), Just-In-Time compiler capable of boosting Python code performace more then 5x times
 * Modularized


## Stream processor example

```python
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
```



## High-level architecture

![Schema of BSPump high-level achitecture](./doc/_static/bspump-architecture.png)


## Licence

BSPump is an open-source software, available under BSD 3-Clause License.
BSPump is a part of Black Swan project, joint effort of Liberty Aces and TeskaLabs.
