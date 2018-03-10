# BSPump: A real-time stream processor for Python 3.5+

## Principles

 * Write once, use many times
 * Simple to use and well documented, so anyone can write their own stream processor
 * Sliding time window
 * Schema-less
 * High performance
 * Asynchronous via Python 3.5+ `async`/`await` and `asyncio`
 * [Event-driven](http://en.wikipedia.org/wiki/Event_driven) / [Reactor pattern](https://en.wikipedia.org/wiki/Reactor_pattern)
 * Single-threaded core but compatible with threads
 * Compatible with [pypy](http://pypy.org), Just-In-Time compiler capable of boosting Python code performace more then 5x times
 * Modularized


## Stream processor example

```python
#!/usr/bin/env python3
import bspump
import bspump.socket
import bspump.common
import bspump.amqp

class SamplePipeline1(bspump.Pipeline):

    def __init__(self, app, pipeline_id, driver):
        super().__init__(app, pipeline_id)
        self.build(
            bspump.socket.TCPStreamSource(app, self),
            bspump.amqp.AMQPSink(app, self, driver)
        )

class SamplePipeline2(bspump.Pipeline):

    def __init__(self, app, pipeline_id, driver):
        super().__init__(app, pipeline_id)
        self.build(
            bspump.amqp.AMQPSource(app, self, driver),
            bspump.common.PPrintSink(app, self)
        )

if __name__ == '__main__':
    app = bspump.BSPumpApplication()

    amqp_driver = bspump.amqp.AMQPDriver(app)
    svc = app.get_service("bspump.PumpService")

    svc.add_pipelines(
        SamplePipeline1(app, 'SamplePipeline1', amqp_driver),
        SamplePipeline2(app, 'SamplePipeline2', amqp_driver),
    )

    app.run()
```


## Licence

BSPump is an open-source software, available under BSD 3-Clause License.
BSPump is a part of Black Swan project, joint effort of Liberty Aces and TeskaLabs.
