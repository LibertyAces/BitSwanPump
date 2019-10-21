from bspump import Sink
import asyncio
import logging


L = logging.getLogger(__name__)


class MongoDBSink(Sink):

    ConfigDefaults = {
        "output_queue_max_size": 100,
        'collection': 'collection',
    }

    def __init__(self, app, pipeline, connection, id=None, config=None):
        super().__init__(app, pipeline, id, config)

        self.Connection = pipeline.locate_connection(app, connection)
        self.Pipeline = pipeline
        self._output_queue = asyncio.Queue()
        self._output_queue_max_size = int(self.Config['output_queue_max_size'])
        self.Collection = self.Config['collection']
        assert (self._output_queue_max_size >= 1), "Output queue max size invalid"
        self._conn_future = None

        self._on_health_check("Connection.open!")

        app.PubSub.subscribe("Application.stop!", self._on_application_stop)
        app.PubSub.subscribe("Application.tick!", self._on_health_check)
        app.PubSub.subscribe("Application.exit!", self._on_exit)

    def _on_health_check(self, message_type):
        if self._conn_future is not None:

            if not self._conn_future.done():
                return

            self._conn_future.result()

            self._conn_future = None

        assert (self._conn_future is None)

        self._conn_future = asyncio.ensure_future(
            self._ingestion(),
            loop=self.Loop
        )

    def _on_application_stop(self, message_type):
        self._output_queue.put_nowait(None)

    async def _on_exit(self, message_type):
        if self._conn_future is not None:
            await asyncio.wait([self._conn_future], return_when=asyncio.ALL_COMPLETED, loop=self.Loop)

    def process(self, context, event: [dict, list]):
        if self._output_queue.qsize() >= self._output_queue_max_size:
            self.Pipeline.throttle(self, True)

        self._output_queue.put_nowait(event)

    async def _ingestion(self):

        db = self.Connection.Client[self.Connection.Database][self.Collection]

        while True:

            item = await self._output_queue.get()
            if self._output_queue.qsize() == self._output_queue_max_size - 1:
                self.Pipeline.throttle(self, False)

            elif item is None:
                break
            elif type(item) == dict:
                await db.insert_one(item)
                self._output_queue.task_done()
            elif type(item) == list and len(item) > 0:
                await db.insert_many(item)
                self._output_queue.task_done()
            else:
                raise TypeError(f"Only dict or list of dicts allowed, {type(item)} supplied")
