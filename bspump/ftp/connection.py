import logging
import sys
import asyncio
import asyncssh
import sys

from ..abc.connection import Connection


L = logging.getLogger(__name__)


class FtpConnection(Connection):
	...

# ConfigDefaults = {
#     'host': 'localhost',
#     'port': 8022, # good to use dynamic ports in range 49152-62535
#     # 'user': '',
#     # 'password': '',
#     'client_keys': '',
#     'process': '',
#     'known_hosts': None, # None not recommended - use 'my_known_hosts' instead
#     'use_preserve': False,
#     'use_recurse': False,
#     'file': '',
#
#
# }
#
#
# def __init__(self, app, id=None, config=None):
#     super().__init__(app, id=id, config=config)
#
#     self._host = self.Config['host']
#     self._port = self.Config['port']
#
#     self._file = self.Config['file']
#     self._preserve = self.Config['use_preserve']
#     self._recurse = self.Config['use_recurse']

# async def start_server():
#     await asyncssh.listen(self._host, self._port, server_host_keys=['ssh_host_key'],
#                           authorized_client_keys='ssh_user_ca',
#                           sftp_factory=True)
#
# loop = asyncio.get_event_loop()
#
# try:
#     loop.run_until_complete(start_server())
# except (OSError, asyncssh.Error) as exc:
#     sys.exit('Error starting server: ' + str(exc))
#
# loop.run_forever()

# def __init__(self, app, id=None, config=None):
#     super().__init__(app, id=id, config=config)
#
#     self._host = self.Config['host']
#
#     self._file = self.Config['file']
#     self._preserve = self.Config['use_preserve']
#     self._recurse = self.Config['use_recurse']
#
#
#
# async def run_client():
#     async with asyncssh.connect('localhost') as conn:
#         async with conn.start_sftp_client() as sftp:
#             await sftp.get(self._file, self._preserve, self._recurse)
#
# try:
#     asyncio.get_event_loop().run_until_complete(run_client())
# except (OSError, asyncssh.Error) as exc:
#     sys.exit('SFTP operation failed: ' + str(exc))


