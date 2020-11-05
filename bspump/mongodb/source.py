""" Module for connecting to Mongo database"""

import logging
from bspump.abc.source import TriggerSource

#

L = logging.getLogger(__name__)


#

class MongoDBSource(TriggerSource):
    """MongoDB database source"""

    def __init__(self, app, pipeline, connection,query_parms=None, id=None, config=None):
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
        self.Loop = app.Loop
        self.QueryParms = query_parms
        self.Connection = pipeline.locate_connection(app, connection)
        self.Database = self.Config['database']
        self.Collection = self.Config['collection']
        self.App = app

    async def cycle(self):
        try:
            db = self.Connection.Client[self.Database]
            coll = db[self.Collection]
            await self.Pipeline.ready()

            q_filter = self.QueryParms.get("filter",None)
            q_projection = self.QueryParms.get("projection",None)
            q_limit = self.QueryParms.get("limit",0)

            cur = coll.find(q_filter,q_projection,0,int(q_limit))
            async for recs in cur:
                await self.process(recs, context={})
        except Exception as ex:
            print(ex)





