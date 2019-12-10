from .trigger import Trigger


class PubSubTrigger(Trigger):


	def __init__(self, app, message_types, pubsub=None, id=None):
		super().__init__(app, id)
		self.PubSub = pubsub if pubsub is not None else app.PubSub

		if isinstance(message_types, str):
			self.PubSub.subscribe(message_types, self.on_message)
		else:
			for message_type in message_types:
				self.PubSub.subscribe(message_type, self.on_message)


	async def on_message(self, message_type):
		self.fire()
