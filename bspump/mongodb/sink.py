from bspump import Sink
import asyncio
import logging


L = logging.getLogger(__name__)


class MongoDBSink(Sink):

    """
    MongoDBSink is a sink processor that forwards the event to a MongoDB specified
    by a MongoDBConnection object.

    MongoDBSink expects either a dictionary or a list of dictionaries as an input.

    Example code can be found in the examples section under bspump-mongo-sink.py

    While the connection defines MongoDB database used, you need to specify particular collection
    inside of this database in the sink itself by modifying the ConfigDefaults while instantiating
    the class.

    """

    ConfigDefaults = {
        "output_queue_max_size": 100,
        'collection': 'collection',
    }

    def __init__(self, app, pipeline, connection, id=None, config=None):
        super().__init__(app, pipeline, id, config)
        # We make use of a connection and pipeline, defined in a different place of the pump.
        self.Connection = pipeline.locate_connection(app, connection)
        self.Pipeline = pipeline

        self._output_queue = asyncio.Queue()
        self._output_queue_max_size = int(self.Config['output_queue_max_size'])
        self.Collection = self.Config['collection']
        assert (self._output_queue_max_size >= 1), "Output queue max size invalid"
        self._conn_future = None

        self._on_health_check("Connection.open!")
        # This part subscribes to outside events used to control the flow of the whole pump.
        # Depending on the specific event, a related class method gets called.
        app.PubSub.subscribe("Application.stop!", self._on_application_stop)
        app.PubSub.subscribe("Application.tick!", self._on_health_check)
        app.PubSub.subscribe("Application.exit!", self._on_exit)

    def _on_health_check(self, message_type):
        # At this point we examine the state of the _conn_future instance variable, queueing _outfluxing
        # in case it is None, returning early if the future is not done and resetting _conn_future to None otherwise.
        if self._conn_future is not None:

            if not self._conn_future.done():
                return

            self._conn_future.result()

            self._conn_future = None

        assert (self._conn_future is None)

        self._conn_future = asyncio.ensure_future(
            self._insert(),
            loop=self.Loop
        )

    def _on_application_stop(self, message_type, counter):
        # On requested stop, we insert 'None' to the FIFO (first in first out) asyncio Queue this means (see later),
        # that no task or item inserted after will be processed.
        self._output_queue.put_nowait(None)

    async def _on_exit(self, message_type):
        # On application exit, we first await completion of all tasks in the queue.
        if self._conn_future is not None:
            await asyncio.wait([self._conn_future], return_when=asyncio.ALL_COMPLETED, loop=self.Loop)

    def process(self, context, event: [dict, list]):
        # This is where we check if the queue is overflowing in which case we apply throttling.
        if self._output_queue.qsize() >= self._output_queue_max_size:
            self.Pipeline.throttle(self, True)
        # Here,  we take the event (in this case it should be either a dictionary or a list of dictionaries,
        # and insert it into the queue to be available to the _outflux method.
        self._output_queue.put_nowait(event)

    async def _insert(self):

        db = self.Connection.Client[self.Connection.Database][self.Collection]

        while True:
            # Here is where we await the event (which in this case contains the data we want to save to the database)
            # to be pulled out of the queue and saved to a local variable.
            item = await self._output_queue.get()
            # We check the queue size and remove throttling if the size is smaller than its defined max size.
            if self._output_queue.qsize() == self._output_queue_max_size - 1:
                self.Pipeline.throttle(self, False)
            # At this point, we check what kind of item we pulled from the queue. If its None, it means we
            # reached what was inserted by _on_application_stop and we break the loop immediately.
            # If this is not the case we continue determining the type of the item and proceed accordingly,
            # including raising a type error, if the type is unexpected.
            if item is None:
                break
            elif type(item) == dict:
                await db.insert_one(item)
                self._output_queue.task_done()
            elif type(item) == list and len(item) > 0:
                await db.insert_many(item)
                self._output_queue.task_done()
            else:
                raise TypeError(f"Only dict or list of dicts allowed, {type(item)} supplied")
