import asab
import asyncio
import logging
import asyncssh

import os

from ..abc.source import Source

#

L = logging.getLogger(__name__)

#

ConfigDefaults = {

	'remote_path': '',
	'local_path': '',
	'preserve': 'False',
	'recurse': 'False',

}

"""

If preserve is True, the access and modification times and permissions of the original file are set on the downloaded file.

If recurse is True and the remote path points at a directory, the entire subtree under that directory is downloaded.

"""


class FTPSource(Source):

	def __init__(self, app, pipeline, connection, id=None, config=None):
		super().__init__(app, pipeline, id=id, config=config)
		self._connection = pipeline.locate_connection(app, connection)
		self.Loop = app.Loop
		self.App = app
		self.Pipeline = pipeline

		self.start(self.Loop)

		self._rem_path = self.Config['remote_path']
		self._loc_path = self.Config['local_path']
		self._preserve = bool(self.Config['preserve'])
		self._recurse = bool(self.Config['recurse'])


	async def main(self):
		await self.Pipeline.ready()
		await self._connection.ConnectionEvent.wait()
		async with self._connection.acquire_connection() as connection:
			async with connection.start_sftp_client() as sftp:
				await sftp.get(self._rem_path, localpath=self._loc_path, preserve=self._preserve, recurse=self._recurse)
				# event = self.reader(self._loc_path)
				# await self.Pipeline.process(event)

	# def reader(self, event): #TODO Do some Process reader of sourced files?
	# 	# fils = [f for f in os.listdir(event) if isfile(os.join(event, f))]
	# 	# for fil in fils:
	# 	fil = event
	# 	with open(fil) as myfile:
	# 		data = myfile.read()
	# 		return data


	# def complete(self):
	# 	try:
	# 		asyncio.get_event_loop().run_until_complete(self.main())
	# 	except (OSError, asyncssh.Error) as exc:
	# 		sys.exit('SSH connection failed: ' + str(exc))














