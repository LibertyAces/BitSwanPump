.. _websocket:

WebSocket Example
=================

This example will show you how can you can connect two pipelines connection using socket.

About
-----

what is socket
--------------

explain server/client consumer/producer
---------------------------------------

The pipeline you will create can be either a server or a client. Server is a script that listens on a certain IP address
and port, client is the one who "connects" to a certain port and wants to connect to the server. Both client and server can
be either consumers, this means that it receives (consumes) the data, and producer which produce the data. The specific
combination of server/client consumer/producers mainly depends on what do you wanna do. In this example we will show both
server/consumer - client/producer type of connection and server/producer - client/consumer connection.

Server consumer
---------------

Server consumer means that this pipeline will be waiting for any client trying to make a connection and if there is a connection
with a client. This server pipeline will use Websocket Source as it Source. Therefore, it will await any incoming data from
the client and propagate it as an event deeper into the pipeline.


To create this kind of pipeline we have to use our WebSocketSource and specify the address and port on which it will listen for
any possible connections.

::

    #!/usr/bin/env python3
    import bspump
    import bspump.common
    import bspump.web
    import bspump.http


    class SamplePipeline(bspump.Pipeline):

        def __init__(self, app, pipeline_id):
            super().__init__(app, pipeline_id)

            self.WebSocketSource = bspump.http.WebSocketSource(app, self)

            self.build(
                self.WebSocketSource,
                bspump.common.PPrintSink(app, self)
            )


    if __name__ == '__main__':
        app = bspump.BSPumpApplication(web_listen="0.0.0.0:8080")

        svc = app.get_service("bspump.PumpService")

        # Construct and register Pipeline
        pl = SamplePipeline(app, 'SamplePipeline')
        svc.add_pipeline(pl)

        app.WebContainer.WebApp.router.add_get('/bspump/ws', pl.WebSocketSource.handler)

        app.run()

The important part is to add

Client producer
---------------


::

    #!/usr/bin/env python3
    import bspump
    import bspump.common
    import bspump.http


    class SamplePipeline(bspump.Pipeline):

        def __init__(self, app, pipeline_id):
            super().__init__(app, pipeline_id)
            self.Counter = 1

            self.Source = bspump.common.InternalSource(app, self)

            self.build(
                self.Source,

                bspump.http.HTTPClientWebSocketSink(app, self, config={
                    'url': 'http://localhost:8080/bspump/ws',
                })

            )

            app.PubSub.subscribe("Application.tick!", self.on_tick)


        async def on_tick(self, message_type):
            if self.is_ready():
                await self.Source.put_async({}, "Tick {}!".format(self.Counter))
                self.Counter += 1


    if __name__ == '__main__':
        app = bspump.BSPumpApplication()

        svc = app.get_service("bspump.PumpService")

        # Construct and register Pipeline
        pl = SamplePipeline(app, 'SamplePipeline')
        svc.add_pipeline(pl)

        app.run()


