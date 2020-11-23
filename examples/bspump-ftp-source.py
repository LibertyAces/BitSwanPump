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

"""
    This example connects to FTP server ,converts filename into bytes and outputs the result into console .
    If the filename is not specified coverts each and every files into bytes and and outputs the result into 
    console .
"""


class MyApplication(BSPumpApplication):

    def __init__(self):
        super().__init__()

        svc = self.get_service("bspump.PumpService")

        #Fill in connection parameters here
        svc.add_connection(bspump.ftp.FTPConnection(self, "FTPConnection" ,
                                                config={ 'hostname': '127.0.0.1',
                                                         'username': 'user',
                                                         'password': 'password',
                                                         'port': 21
                                                         }) )
        svc.add_pipeline(MyPipeline0(self))

class MyPipeline0(Pipeline):
    def __init__(self, app, pipeline_id=None):
        super().__init__(app, pipeline_id)
        #Default is root ,fill in specific path inside FTP if any remote_path'
        self.build(
            bspump.ftp.FTPSource(app, self, "FTPConnection", config={'remote_path': '/',
                                                                     'mode': 'r' })
                .on(bspump.trigger.RunOnceTrigger(app)),
            bspump.common.PPrintSink(app, self),
        )

if __name__ == '__main__':
    app = MyApplication()
    app.run()
