import logging
import bspump.ssh
import datetime
import bspump
import bspump.mongodb
import bspump.ssh
import bspump.common
import bspump.file
import bspump.trigger

###

L = logging.getLogger(__name__)

"""

	Config file for SSH connection should look like this:
	# SSH Connection

	[connection:SSHConnection]
	host=remotehost
	port=22
	user=remoteuser
	password=p455w0rd
	known_hosts=.ssh/known_hosts
	client_host_keysign=/path/to/dir/with/ssh-keysign
	client_host_keys=skey


..

	If do not know the known_hosts or client_host_keys, leave it empty or do not append it to a Config file.
	If do not know the path to the directory with keys of client_host_keysign, do not append it to a Config file or
	set it to 0 (zero).

	Add conf file to ../etc/

    This example connects to mongodb. 
        #host = mongodb://127.0.0.1:27017
        #databaseb=users
        #collections=user_location 
    query's the database according to the parameters passed into query_parms 
    and outputs the result into a file though SFTP. 
"""




class SamplePipeline(bspump.Pipeline):

    def __init__(self, app, pipeline_id = None):
        super().__init__(app, pipeline_id)

        self.fileextjson = ".json"

        # Set the file name as "todays-date.json" for sftpsink
        self.jsonfilename = datetime.datetime.now().strftime('%d-%m-%Y') + self.fileextjson
        print(self.jsonfilename)

        query_parms = {
        }
        #run the application bspump-es-source.py -c ./etc/site.cofig
        self.build(
            bspump.mongodb.MongoDBSource(app, self, "MongoDBConnection", query_parms=query_parms,
                                         config={'database':'users',
				                                'collection':'user_location',
                                                 }).on(bspump.trigger.PeriodicTrigger(app,5 )),

            bspump.common.DictToJsonBytesParser(app, self),
            bspump.ssh.SFTPSink(app, self, "SSHConnection2" ,config={
                'remote_path': '/tmp/bspump_ssh/',
				'filename': 'testfile',
				'mode': 'a',
            })
        )

if __name__ == '__main__':
    app = bspump.BSPumpApplication()
    svc = app.get_service("bspump.PumpService")

    # Make connection to SSH
    svc.add_connection(
        bspump.ssh.SSHConnection(app, "SSHConnection2" ,config={
            "host": "bandit.labs.overthewire.org",
			"user": "bandit0",
			"password": "bandit0",
			"port": 2220,
        })
    )
    # Make connection to localhost Mongo
    svc.add_connection(bspump.mongodb.MongoDBConnection(app,"MongoDBConnection" ,config={
        "host": "mongodb://127.0.0.1:27017"}))

    # Construct and register Pipeline
    pl = SamplePipeline(app, 'SamplePipeline')
    svc.add_pipeline(pl)

    pl.PubSub.publish("go!")

    app.run()
