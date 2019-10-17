from bspump import Sink
import asyncio
import logging


L = logging.getLogger(__name__)


class MongoSink(Sink):

    def __init__(self, app, pipeline, connection, id=None, config=None):
        super().__init__(app, pipeline, id, config)

        self.Connection = pipeline.locate_connection(app, connection)
        self._output_queue = asyncio.Queue()
        self._output_queue_max_size = int(10)
        self._conn_future = None

        self._on_health_check('connection.open!')

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
            self.insert_item(),
            loop=self.Loop
        )

    def _on_application_stop(self):
        self._output_queue.put_nowait((None, None))

    async def _on_exit(self):
        if self._conn_future is not None:
            await asyncio.wait([self._conn_future], return_when=asyncio.ALL_COMPLETED, loop=self.Loop)

    def process(self, context, event: [dict, list]):
        self._output_queue.put_nowait(event)

    async def insert_item(self):

        db = self.Connection.Client["test_test"]

        what_for = await self._output_queue.get()
        await db.test_collection.insert_one(what_for)
        self._output_queue.task_done()
