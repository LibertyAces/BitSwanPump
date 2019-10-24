import logging
import bspump
import bspump.common
import bspump.random
import bspump.trigger
import bspump.ssh
import time


###

L = logging.getLogger(__name__)

###


class SamplePipeline(bspump.Pipeline):

	"""

	Config file for SSH connection should look like this:
	# SSH Connection

	[connection:SSHConnection]
	host=remotehost
	port=22
	user=remoteuser
	password=p455w0rd
	known_hosts=.ssh/known_hosts
	client_host_keysign=/path/to/dir/with/keys
	client_host_keys=skey


..

	If do not know the known_hosts or client_host_keys, leave it empty or do not append it to a Config file.
	If do not know the path to the directory with keys of client_host_keysign, do not append it to a Config file or
	set it to 0 (zero).

	Add conf file to ../etc/

	"""

	def __init__(self, app, pipeline_id=None):
		super().__init__(app, pipeline_id)
		upper_bound = int(time.time())
		lower_bound = upper_bound - 100500
		self.build(
			bspump.random.RandomSource(app, self, choice=['ab', 'bc', 'cd', 'de', 'ef', 'fg'], config={'number': 150}
									   ).on(bspump.trigger.OpportunisticTrigger(app, chilldown_period=60)),
			bspump.random.RandomEnricher(app, self, config={
				'field': '@timestamp',
				'lower_bound': lower_bound,
				'upper_bound': upper_bound
			}),
			bspump.common.DictToJsonBytesParser(app,self),
			# bspump.common.StringToBytesParser(app, self),
			bspump.ssh.SFTPSink(app, self, "SSHConnection2", config={'remote_path': '/test3/',
																	'filename': 'testname',
																	'mode': 'a',
																	})
		)


if __name__ == '__main__':
	app = bspump.BSPumpApplication()

	svc = app.get_service("bspump.PumpService")

	svc.add_connection(
		bspump.ssh.SSHConnection(app, "SSHConnection2")
	)

	# Construct and register Pipeline
	pl = SamplePipeline(app, 'SamplePipeline')
	svc.add_pipeline(pl)

	app.run()

