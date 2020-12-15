#!/usr/bin/env python3

from bspump import BSPumpApplication, Pipeline

import bspump.trigger
import bspump.common
import bspump.abc
import bspump.mongodb
import logging

##
L = logging.getLogger(__name__)

"""
    This example connects to mongodb running on our oilvan server. 
        #host = //127.0.0.1:27017
        #databaseb=users
        #collections=user_location
    query's the database according to the parameters passed into query_parms 
    and outputs the result into console 
"""


class MyApplication(BSPumpApplication):

    def __init__(self):
        super().__init__()
        svc = self.get_service("bspump.PumpService")
        svc.add_connection(bspump.mongodb.MongoDBConnection(self, config={
            "host": "mongodb://127.0.0.1:27017"}))
        svc.add_pipeline(MyPipeline0(self))


class MyPipeline0(Pipeline):

    def __init__(self, app, pipeline_id=None):
        super().__init__(app, pipeline_id)

        """
        query_parms takes three parms (filter,projection,number of records). If you don't pass either of these.
        Default is None. 

        Example on how to use queryparms 

        query_parms = {
         "filter": { '_id': 'E48D8C-hAP%20ac%C2%B2-D7160BFE779D'},
         "projection" : "{ '_timestamp' }",
        "limit": "0"
         }

        """
        query_parms = {}

        self.build(
            bspump.mongodb.MongoDBSource(app, self, "MongoDBConnection", query_parms=query_parms,
                                         config={'database':'users',
				                                'collection':'user_location'
                                                 }).on(bspump.trigger.RunOnceTrigger(app)),
            bspump.common.PPrintSink(app, self))


if __name__ == '__main__':
    app = MyApplication()
    app.run()
