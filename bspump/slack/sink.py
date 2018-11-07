from ..abc.sink import Sink


class SlackAbcSink(Sink):

	def __init__(self, app, pipeline, connection, id=None, config=None):
		super().__init__(app, pipeline, id=id, config=config)

		self.Connection = pipeline.locate_connection(app, connection)

		app.PubSub.subscribe("SlackConnection.pause!", self._connection_throttle)
		app.PubSub.subscribe("SlackConnection.unpause!", self._connection_throttle)


	def _connection_throttle(self, event_name, connection):
		if connection != self.Connection:
			return

		if event_name == "SlackConnection.pause!":
			self.Pipeline.throttle(self, True)
		elif event_name == "SlackConnection.unpause!":
			self.Pipeline.throttle(self, False)
		else:
			raise RuntimeError("Unexpected event name '{}'".format(event_name))


class SlackTextSink(SlackAbcSink):

	def process(self, context, event):
		'''
		Param 'event' must be a string
		'''
		msg = {'text': str(event)}
		self.Connection.consume(msg)


class SlackMessageSink(SlackAbcSink):

	def process(self, context, event):
		'''
		Param 'event' must be a Slack message (https://api.slack.com/docs/messages)
		It must contains at least keys 'text' or 'attachments'
		Example:
			{
				"text": "This is text example!",
				"attachments": [
					{
						"title": "This is attachments title",
						"fields": [
							{
								"title": "Volume",
								"value": "1",
								"short": true
							}
						]
					}
				]
			}
		'''

		self.Connection.consume(event)
