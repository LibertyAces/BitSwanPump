import aiohttp
import logging
import asyncio
import json
from ..abc.connection import Connection
import smtplib
from email.mime.text import MIMEText
import aiosmtplib
from pprint import pprint

L = logging.getLogger(__name__)



class SmtpConnection(Connection):

	ConfigDefaults = {
		'smtp_server': '',
		'port':None,
		'use_tls':False,
		'use_start_tls':False,
		'login':'',
		'password':'',
		'sender_email':'',
		'receiver_email':'',
		'output_queue_max_size': 10
	}

	def __init__(self, app, connection_id, config=None):
		super().__init__(app, connection_id, config=config)

		self.Smtp_server = self.Config['smtp_server']
		self.Port = self.Config['port']
		self.Use_tls = self.Config.getboolean('use_tls')
		self.Use_start_tls = self.Config.getboolean('use_start_tls')

		self.Login = self.Config['login']
		self.Password = self.Config['password']


		self.Sender_email = self.Config['sender_email']
		self.Receiver_email = self.Config['receiver_email']

		print('*' * 50)
		print ('self.Use_start_tls',self.Use_start_tls)
		print('self.Use_tls', self.Use_tls)
		print('self.Login', self.Login)
		print('self.Password', self.Password)
		print (self.Login != None)
		print(self.Login == None)
		print ('empty string')
		print(self.Login != '')
		print(self.Login == '')
		print('string None')
		print(self.Login != 'None')
		print(self.Login == 'None')
		print (type (self.Login))
		print('*' * 50)

		self.Loop = app.Loop
		self.PubSub = app.PubSub

		self._output_queue_max_size = int(self.Config['output_queue_max_size'])
		self._output_queue = asyncio.Queue(loop=app.Loop, maxsize=self._output_queue_max_size+1)
		self.LoaderTask = asyncio.ensure_future(self._loader(), loop=self.Loop)

		self.PubSub.subscribe("Application.exit!", self._on_exit)


	async def _on_exit(self, event_name):
		# Wait till the _loader() terminates
		pending = [self.LoaderTask]
		while len(pending) > 0:
			# By sending None via queue, we signalize end of life
			await self._output_queue.put(None)
			done, pending = await asyncio.wait(pending, return_when=asyncio.FIRST_COMPLETED)


	def consume(self, mail_message):
		# mail_message = json.dumps(mail_message)
		self._output_queue.put_nowait(mail_message)

		if self._output_queue.qsize() == self._output_queue_max_size:
			self.PubSub.publish("MailConnection.pause!", self)


	# async def _loader(self):
	# 	while True:
	# 		mail_message = await self._output_queue.get()
	# 		if mail_message is None:
	# 			break
	#
	# 		if self._output_queue.qsize() == self._output_queue_max_size - 1:
	# 			self.PubSub.publish("MailConnection.unpause!", self, asynchronously=True)
	#
	# 		message = str(mail_message)
	# 		print(message + "..... jenze kapri smrdi")
	#
	# 		with smtplib.SMTP(self.Smtp_server, self.Port) as server:
	# 			server.helo()
	# 			server.sendmail(self.Sender_email, self.Receiver_email, message)
	#
	# 		# async with session.post(self.Url, data=mail_message, headers={'content-type': 'application/json'}) as resp:
	# 		# 	resp_body = await resp.text()
	# 		# 	if resp.status != 200:
	# 		# 		L.error("Failed to send Mail message status:{} body:{}".format(resp.status, resp_body))
	# 		#
	# 		# 		# Requeue the message, wait a bit and try again
	# 		# 		self._output_queue.put_nowait(mail_message)
	# 		# 		await asyncio.sleep(5)



	async def _loader(self):
		loop = self.Loop

		smtp = aiosmtplib.SMTP(
			hostname=self.Smtp_server,
			port=self.Port,
			loop=loop,
			use_tls=self.Use_tls
		)

		await smtp.connect()

		if self.Use_start_tls == True:
			await smtp.starttls()


		if self.Login != '' and self.Password != '':
			await smtp.auth_login (self.Login, self.Password)


		while True:
				message_text = await self._output_queue.get()
				if message_text is None:
					break

				if self._output_queue.qsize() == self._output_queue_max_size - 1:
					self.PubSub.publish("MailConnection.unpause!", self, asynchronously=True)

				print(message_text)

				message = MIMEText(message_text)
				message["From"] = self.Sender_email
				message["To"] = self.Receiver_email
				message["Subject"] = "BSPump SMTPSink message"

				await smtp.send_message(message)