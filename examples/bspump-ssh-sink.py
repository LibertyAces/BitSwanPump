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
		Config file for FTP connection should look like this:
		# FTP Connection

		[connection:SSHConnection]
		host=bandit.labs.overthewire.org
		port=2220
		user=bandit0
		password=bandit0
		known_hosts_path=path1,path2

		#################################

		If do not know the known_hosts_path, leave it empty or do not append it to a Config file.

		conf file in ../etc/



	"""

	def __init__(self, app, pipeline_id=None):
		super().__init__(app, pipeline_id)
		upper_bound = int(time.time())
		lower_bound = upper_bound - 100500
		self.build(
			bspump.random.RandomSource(app, self, choice=['ab', 'bc', 'cd', 'de', 'ef', 'fg'], config={'number': 450}
									   ).on(bspump.trigger.OpportunisticTrigger(app, chilldown_period=60)),
			bspump.random.RandomEnricher(app, self, config={
				'field': '@timestamp',
				'lower_bound': lower_bound,
				'upper_bound': upper_bound
			}),
			bspump.common.DictToJsonBytesParser(app,self),
			# bspump.common.StringToBytesParser(app, self),
			bspump.ssh.SFTPSink(app, self, "SSHConnection2", config={'remote_path': '/test_folder/',
																	'host': '10.17.106.232',#'demo.wftpserver.com',
																	 'rand_int': 1000,
																	 'encoding': 'utf-8',
																	 'mode': 'a',
																	 'out_type': 'string',
																	 'output_queue_max_size': 1000,})
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

