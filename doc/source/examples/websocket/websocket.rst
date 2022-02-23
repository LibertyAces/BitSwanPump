.. _websocket:

WebSocket Example
=================

This example will show you how can you can connect two pipelines connection using socket server connection.


what is socket
--------------



explain server/client consumer/producer
---------------------------------------

The pipeline you will create can be either a server or a client. Server is a script that listens on a certain IP address
and port, client is the one who "connects" to a certain port of the server. Both client and server can be either consumers,
meaning that consumer (consumes) the data, and producer is the one who produce the data. The specific combination of server/client
consumer/producers mainly depends on what do you wanna do. In this example we will show both server/consumer - client/producer
type of connection and server/producer - client/consumer connection.

Server consumer
---------------

Server consumer means that this pipeline will be waiting for any client trying to make a connection and if there is a connection
with a client the server will get the incoming data into its pipeline. This server pipeline will use Websocket Source as its Source.

To create this kind of pipeline we have to use our WebSocketSource and specify the address and port on which it will listen for
any possible connections. In this example we will run both pipelines on localhost, so you do not have to waste your time setting up your own network.

::

    #!/usr/bin/env python3
    import bspump
    import bspump.common
    import bspump.web
    import bspump.http


    class SamplePipeline(bspump.Pipeline):

        def __init__(self, app, pipeline_id):
            super().__init__(app, pipeline_id)



            self.build(
                bspump.http.WebSocketSource(app, self),
                bspump.common.PPrintSink(app, self)
            )


    if __name__ == '__main__':
        app = bspump.BSPumpApplication(web_listen="0.0.0.0:8080") #set web_listen variable to the address you want

        svc = app.get_service("bspump.PumpService")

        # Construct and register Pipeline
        pl = SamplePipeline(app, 'SamplePipeline')
        svc.add_pipeline(pl)

        #you have to use add_get method to set up address using the handler.
        app.WebContainer.WebApp.router.add_get('/bspump/ws', pl.WebSocketSource.handler)

        app.run()

You can copy-paste the code above. The pipeline is really simple the only thing you have to do is to add WebSocket Source.
Just make sure to set up the ``web_listen`` variable in the ``BSPumpApplication`` object, and do not forget that you have to call the ``add_get`` method **TODO**

Now you can run the script and your server should be running listening for any possible connections.

Client producer
---------------

We have a running server, so now we have to create a client that can connect to the server and feed it with the data.


::

    #!/usr/bin/env python3
    import bspump
    import bspump.common
    import bspump.http
    import bspump.trigger


    class SamplePipeline(bspump.Pipeline):

        def __init__(self, app, pipeline_id):
            super().__init__(app, pipeline_id)
            self.Counter = 1

            # self.Source = bspump.common.InternalSource(app, self)

            self.build(
                bspump.http.HTTPClientSource(app, self, config={
                    'url': 'https://api.coindesk.com/v1/bpi/currentprice.json'
                    # Trigger that triggers the source every second (based on the method parameter)
                }).on(bspump.trigger.PeriodicTrigger(app, 5)),

                bspump.http.HTTPClientWebSocketSink(app, self, config={
                    'url': 'http://127.0.0.1:8080/bspump/ws',
                })

            )

    if __name__ == '__main__':
        app = bspump.BSPumpApplication()

        svc = app.get_service("bspump.PumpService")

        # Construct and register Pipeline
        pl = SamplePipeline(app, 'SamplePipeline')
        svc.add_pipeline(pl)

        app.run()

Creating the client is much more easier than the server. All you have to do is to use ``HTTPClientSocketSink`` with config
where you specify the url of the server you want to connect to. In this case it is ``http://127.0.0.1:8080/bspump/ws``

Server Producer
---------------

TODO

Client Consumer
---------------

TODO

what next
---------

This example should have you given an idea how to use and connect pipelines using socket connection.