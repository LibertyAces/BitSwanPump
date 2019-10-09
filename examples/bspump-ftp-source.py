#!/usr/bin/env python3
import logging

import bspump
import bspump.common
import bspump.common
import bspump.file
import bspump.random
import bspump.trigger
import bspump.ftp



###

L = logging.getLogger(__name__)

###


class SamplePipeline(bspump.Pipeline):
	"""
		Config file for FTP connection should look like this:
		# FTP Connection

		[connection:FTPConnection]
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

		self.build(
			# bspump.ftp.FTPSource(app, self, "FTPConnection1", config={'remote_path': '/home/bandit0/readme',
			# 														 'local_path': '/home/doma/projects/',
			# 														 'preserve': False,
			# 														 'recurse': False,}),
			# bspump.common.PPrintProcessor(app, self),
			#
			# bspump.common.PPrintSink(app, self),
			bspump.random.RandomSource(app, self, choice=['a', 'b', 'c'], config={
				'number': 5
			}).on(bspump.trigger.OpportunisticTrigger(app, chilldown_period=10)),
			bspump.ftp.FTPSink(app, self, "FTPConnection2", config={'remote_path': '/upload/',
																	'local_path': '/home/doma/projects/readme_test.txt',
																	'preserve': False,
																	'recurse': False,}), #FTPSink not established and fully fucntionable yet
		)


if __name__ == '__main__':
	app = bspump.BSPumpApplication()

	svc = app.get_service("bspump.PumpService")

	svc.add_connection(
		# bspump.ftp.FTPConnection(app, "FTPConnection1"),
		bspump.ftp.FTPConnection(app, "FTPConnection2")
	)

	# Construct and register Pipeline
	pl = SamplePipeline(app, 'SamplePipeline')
	svc.add_pipeline(pl)

	app.run()