import asyncio
import email.mime.text
import logging

import aiosmtplib

from ..abc.connection import Connection

L = logging.getLogger(__name__)


class SmtpConnection(Connection):

	ConfigDefaults = {
		'server': '',
		'port': 587,
		'use_tls': False,
		'use_start_tls': False,
		'login': '',
		'password': '',
		'from': '',
		'to': '',
		'cc': '',
		'bcc': '',
		'subject': 'Mail from ASAB',
		'output_queue_max_size': 10
	}

	def __init__(self, app, id=None, config=None):
		super().__init__(app, id=id, config=config)

		self.Server = self.Config['server']
		self.Port = self.Config['port']
		self.UseTLS = self.Config.getboolean('use_tls')
		self.Use_STARTTLS = self.Config.getboolean('use_start_tls')

		self.Login = self.Config['login']
		self.Password = self.Config['password']


		self.From = self.Config['from']
		self.To = self.Config['to']
		self.Cc = self.Config['cc']
		self.Bcc = self.Config['bcc']

		self.Subject = self.Config['subject']

		self.Smtp = None
		self.Loop = app.Loop
		self.PubSub = app.PubSub

		self._output_queue_max_size = int(self.Config['output_queue_max_size'])
		self._output_queue = asyncio.Queue(loop=app.Loop, maxsize=self._output_queue_max_size + 1)
		self.LoaderTask = asyncio.ensure_future(self._loader(), loop=self.Loop)

		self.PubSub.subscribe("Application.exit!", self._on_exit)


	async def _on_exit(self, event_name):
		# Wait till the _loader() terminates
		pending = [self.LoaderTask]
		while len(pending) > 0:
			# By sending None via queue, we signalize end of life
			await self._output_queue.put(None)
			done, pending = await asyncio.wait(pending, return_when=asyncio.FIRST_COMPLETED)
			if self.Smtp is not None:
				self.Smtp.close()


	def consume(self, mail_message):
		self._output_queue.put_nowait(mail_message)

		if self._output_queue.qsize() == self._output_queue_max_size:
			self.PubSub.publish("SMTPConnection.pause!", self)


	async def _loader(self):
		loop = self.Loop

		self.Smtp = aiosmtplib.SMTP(
			hostname=self.Server,
			port=self.Port,
			loop=loop,
			use_tls=self.UseTLS
		)

		await self.Smtp.connect()

		if self.Use_STARTTLS is True:
			await self.Smtp.starttls()


		if self.Login != '' and self.Password != '':
			await self.Smtp.auth_login(self.Login, self.Password)


		while True:
			message_text = await self._output_queue.get()
			if message_text is None:
				break

			if self._output_queue.qsize() == self._output_queue_max_size - 1:
				self.PubSub.publish("SMTPConnection.unpause!", self, asynchronously=True)

			message = email.mime.text.MIMEText(message_text)
			message["From"] = self.From
			message["To"] = self.To
			message["Subject"] = self.Subject
			if self.Cc != '':
				message["Cc"] = self.Cc
			if self.Bcc != '':
				message["Bcc"] = self.Bcc



			smtp_response, resp_text = await self.Smtp.send_message(message)
			# TODO: Not ideal way of the error detection, we need to investigate and refactor this.
			if resp_text[:2].lower() != 'ok':
				L.error(f"Failed to send message: {resp_text}:{smtp_response}")
