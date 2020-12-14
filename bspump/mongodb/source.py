""" Module for connecting to Mongo database"""
import asyncio
import logging
from bspump.abc.source import TriggerSource

#

L = logging.getLogger(__name__)


#

class MongoDBSource(TriggerSource):
    """MongoDB database source"""

    ConfigDefaults = {
        "output_queue_max_size": 2,
        'database': '',
        'collection': '',
    }

    def __init__(self, app, pipeline, connection, query_parms=None, id=None, config=None):
        """
        Create new instance
            Parameters:
                app (Application): application
                pipeline (PipeLone): pipeline
                connection (Connection): Connection to the database
                query_parms (Dictionary): Query parameters (filter,projection,number of records)
                id (int): Id
                config (Dictionary): Connection configuration
        """

        super().__init__(app, pipeline, id=id, config=config)

        self.Pipeline = pipeline
        self._output_queue = asyncio.Queue()
        self._output_queue_max_size = int(self.Config['output_queue_max_size'])
        self.QueryParms = query_parms
        self.Connection = pipeline.locate_connection(app, connection)
        self.Database = self.Config['database']
        self.Collection = self.Config['collection']
        self._conn_future = None

        # Subscribe
        self._on_health_check("Connection.open!")
        app.PubSub.subscribe("Application.tick!", self._on_health_check)
        app.PubSub.subscribe("Application.stop!", self._on_application_stop)
        app.PubSub.subscribe("Application.exit!", self._on_exit)

    def _on_health_check(self, message_type):

        if self._conn_future is not None:

            if not self._conn_future.done():
                return

            self._conn_future.result()

            self._conn_future = None

        assert (self._conn_future is None)

        self._conn_future = asyncio.ensure_future(
            self.cycle(),
            loop=self.Loop
        )

    def _on_application_stop(self, message_type, counter):
        self._output_queue.put_nowait(None)

    async def _on_exit(self, message_type):
        if self._conn_future is not None:
            await asyncio.wait([self._conn_future], return_when=asyncio.ALL_COMPLETED, loop=self.Loop)

    async def cycle(self):
        db = self.Connection.Client[self.Database]

        # We check the queue size and remove throttling if the size is smaller than its defined max size.
        if self._output_queue.qsize() == self._output_queue_max_size - 1:
            self.Pipeline.throttle(self, False)

        coll = db[self.Collection]
        await self.Pipeline.ready()

        # query parms
        q_filter = self.QueryParms.get("filter", None)
        q_projection = self.QueryParms.get("projection", None)
        q_limit = self.QueryParms.get("limit", 0)

        cur = coll.find(q_filter, q_projection, 0, int(q_limit))
        async for recs in cur:
            pass
            await self.process(recs, context={})
