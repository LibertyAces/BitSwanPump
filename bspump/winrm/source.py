import logging

import itertools
import os
import json

import urllib3
import urllib3.connectionpool

import asyncio

import winrm
from winrm.exceptions import WinRMOperationTimeoutError


from ..abc.source import TriggerSource

#

L = logging.getLogger(__name__)

#


class WinRMSource(TriggerSource):
	"""
	WinRMSource remotely connects to a Windows Server via WS-Management and runs the specified command.
	"""

	ConfigDefaults = {
		"endpoint": "http://127.0.0.1:5985/wsman",  # WS-Management endpoint
		"transport": "ntlm",  # Using NTLM authentication

		"server_cert_validation": "ignore",  # Skipping certificate validation
		"ca_trust_path": "legacy_requests",  # See https://github.com/diyan/pywinrm/blob/master/winrm/protocol.py
		"cert_pem": "",  # File path
		"cert_key_pem": "",  # File path

		"username": "",  # <DOMAIN>\<USER>
		"password": "",

		"command": "wevtutil qe system /c:500 /rd:false",  # The user must be in "Event Log Readers group"
		"duplicity_check": True,  # Check duplicities
		"encoding": "utf-8",  # Encoding of the output

		"last_value_storage": "/data/winrm_last_value_storage.json",  # Last value storage
		"sleep": 0.01  # seconds
	}

	EmptyList = []

	def __init__(self, app, pipeline, id=None, config=None):
		super().__init__(app, pipeline, id=id, config=config)

		# Windows sometimes sends invalid/empty headers,
		# which may cause warnings, especially when using
		# NTLM together with HTTP and not HTTPS, see:
		# https://github.com/diyan/pywinrm/issues/269
		urllib3.connectionpool.log.addFilter(WindowsSuppressFilter())

		# Create connection protocol
		self.Protocol = WinRMProtocol(
			endpoint=self.Config["endpoint"],
			transport=self.Config["transport"],
			server_cert_validation=self.Config["server_cert_validation"],
			ca_trust_path=self.Config["ca_trust_path"],
			cert_pem=self.Config["cert_pem"] if len(self.Config["cert_pem"]) > 0 else None,
			cert_key_pem=self.Config["cert_key_pem"] if len(self.Config["cert_key_pem"]) > 0 else None,
			username=self.Config["username"],
			password=self.Config["password"],
		)

		# Open the shell
		self.ShellId = self.Protocol.open_shell()

		# Obtain command and encoding from the config
		self.Command = self.Config["command"]
		self.Encoding = self.Config["encoding"]
		self.Sleep = float(self.Config["sleep"])

		# Duplicities
		self.DuplicityCheck = self.Config.getboolean("duplicity_check")

		# Load last value from file storage
		self.LastValue = None
		self.LastValueStorage = self.Config["last_value_storage"]
		if os.path.exists(self.LastValueStorage) and not os.path.isdir(self.LastValueStorage):
			with open(self.LastValueStorage, "r") as last_value_file:
				self.LastValue = json.loads(last_value_file.read())["last_value"]

		# Subscribe to exit to close the shell eventually
		app.PubSub.subscribe("Application.exit!", self._on_exit)

	async def _on_exit(self, event_name):
		# Close the shell
		self.Protocol.close_shell(self.ShellId)

		# Save the last value into persistent storage
		if self.LastValue is not None:
			with open(self.LastValueStorage, "w") as last_value_file:
				last_value_file.write(json.dumps({"last_value": self.LastValue}))

	async def cycle(self, *args, **kwags):
		# Run the command remotely
		command_id = self.Protocol.run_command(self.ShellId, self.Command)

		# Obtain the output from the command
		command_done = False
		while not command_done:

			std_out, std_err, status_code, command_done = self.Protocol.get_command_output_nowait(self.ShellId, command_id)

			# Log errors
			if std_err is not None and len(std_err) > 0:
				L.error("Error occurred in WinRMSource for command '{}' with status code '{}': '{}'".format(
					self.Command, status_code, std_err
				))

			# Process the output
			if std_out is not None and len(std_out) > 0:
				output = std_out.decode(self.Encoding)
				lines = output.replace("\r", "").split("\n")

				# Check duplicities
				if self.DuplicityCheck:
					if self.LastValue is not None:
						try:
							index = self.rindex(lines, self.LastValue)
							if index == (len(lines) - 1):
								lines = self.EmptyList
							else:
								lines = lines[(index + 1):]
						except ValueError:
							pass

				# Put the output of the command to the pipeline
				for line in lines:
					if len(line) > 0:
						await self.process(line, context={
							"status_code": status_code
						})
						self.LastValue = line

				# Sleep for some time
				await asyncio.sleep(self.Sleep)

		# Cleanup the command
		self.Protocol.cleanup_command(self.ShellId, command_id)

	@staticmethod
	def rindex(lst, item):
		def index_ne(x):
			return lst[x] != item
		try:
			return next(itertools.dropwhile(index_ne, reversed(range(len(lst)))))
		except StopIteration:
			raise ValueError("rindex(lst, item): item not in list")


class WindowsSuppressFilter(logging.Filter):
	"""
	Suppress WS-Management related logs.
	"""

	def filter(self, record):
		return 'wsman' not in record.getMessage()


class WinRMProtocol(winrm.protocol.Protocol):
	"""
	Custom implementation of get command output method.
	"""

	def get_command_output_nowait(self, shell_id, command_id):
		stdout_buffer, stderr_buffer = [], []
		command_done = False
		return_code = None
		try:
			stdout, stderr, return_code, command_done = \
				self._raw_get_command_output(shell_id, command_id)
			stdout_buffer.append(stdout)
			stderr_buffer.append(stderr)
		except WinRMOperationTimeoutError:
			# this is an expected error when waiting for a long-running process, just silently retry
			pass
		return b''.join(stdout_buffer), b''.join(stderr_buffer), return_code, command_done
