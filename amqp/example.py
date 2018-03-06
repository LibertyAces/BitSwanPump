class PipelineWithRabbitMQ(bspump.Pipeline):

	def __init__(self, app, pipeline_id):
		# Create queue
		# Use queue to create the driver
		self.driver = amqp.driver.AMQPDriver()
		super().__init__(app, pipeline_id)
		
		

	def construct(self, app):
		# Use queue to create the driver
		self.set_source(RabbitMQSource(app, self, self.driver))

		# Processors
		self.append_processor(Sink(app, self))
