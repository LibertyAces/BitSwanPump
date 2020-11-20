#!/usr/bin/env python3

from bspump import BSPumpApplication, Pipeline
import bspump.ftp
import bspump.trigger
import bspump.common
import bspump.abc
import bspump.mongodb
import logging

##
L = logging.getLogger(__name__)

##

class MyApplication(BSPumpApplication):

    def __init__(self):
        super().__init__()

        svc = self.get_service("bspump.PumpService")
        svc.add_connection(bspump.ftp.FTPConnection(self, "FTPConnection" ,
                                                config={ 'hostname': 'localhost',
                                                         'username': 'user',
                                                         'password': 'password',}) )

        svc.add_pipeline(MyPipeline0(self))

class MyPipeline0(Pipeline):
    def __init__(self, app, pipeline_id=None):
        super().__init__(app, pipeline_id)

        self.build(
            bspump.ftp.FTPSource(app, self, "FTPConnection", config={'remote_path': '/',})
                .on(bspump.trigger.RunOnceTrigger(app)),
            bspump.common.PPrintSink(app, self),
        )

if __name__ == '__main__':
    app = MyApplication()
    app.run()
