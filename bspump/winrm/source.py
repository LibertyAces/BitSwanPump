import logging

import urllib3
import urllib3.connectionpool

import winrm

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
		"#": "legacy_requests",  # See https://github.com/diyan/pywinrm/blob/master/winrm/protocol.py
		"cert_pem": "",  # File path
		"cert_key_pem": "",  # File path

		"username": "",  # <DOMAIN>\<USER>
		"password": "",

		"command": "wevtutil qe system /c:500 /rd:false",  # The user must be in "Event Log Readers group"
		"duplicity_check": True,  # Check duplicities
		"encoding": "utf-8",  # Encoding of the output
	}

	def __init__(self, app, pipeline, id=None, config=None):
		super().__init__(app, pipeline, id=id, config=config)

		# Windows sometimes sends invalid/empty headers,
		# which may cause warnings, especially when using
		# NTLM together with HTTP and not HTTPS, see:
		# https://github.com/diyan/pywinrm/issues/269
		urllib3.connectionpool.log.addFilter(WindowsSuppressFilter())

		# Create connection protocol
		self.Protocol = winrm.protocol.Protocol(
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

		# Duplicities
		self.DuplicityCheck = self.Config.getboolean("duplicity_check")
		self.LastValue = None

		# Subscribe to exit to close the shell eventually
		app.PubSub.subscribe("Application.exit!", self._on_exit)

	async def _on_exit(self, event_name):
		self.Protocol.close_shell(self.ShellId)

	async def cycle(self, *args, **kwags):
		# Run the command remotely
		command_id = self.Protocol.run_command(self.ShellId, self.Command)

		# Obtain the output from the command
		std_out, std_err, status_code = self.Protocol.get_command_output(self.ShellId, command_id)

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
						index = lines.index(self.LastValue)
						lines = lines[index:]
					except ValueError:
						pass

			# Put the output of the command to the pipeline
			for line in lines:
				if len(line) > 0:
					await self.process(line, context={
						"status_code": status_code
					})
					self.LastValue = line

		# Cleanup the command
		self.Protocol.cleanup_command(self.ShellId, command_id)


class WindowsSuppressFilter(logging.Filter):
	"""
	Suppress WS-Management related logs.
	"""

	def filter(self, record):
		return 'wsman' not in record.getMessage()
