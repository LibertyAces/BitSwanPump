import bspump
from bspump.kafka import KafkaTopicInitializer


"""
KafkaTopicInitializer scans a JSON or YAML file for Kafka topics and their configurations. 
It checks whether those topics exist on configured Kafka server and initializes them if they don't.

See `examples/data/kafka-topic-config.yml` for an example topic config file.
"""

if __name__ == '__main__':
	app = bspump.BSPumpApplication()

	svc = app.get_service("bspump.PumpService")

	# Create a KafkaConnection
	svc.add_connection(
		bspump.kafka.KafkaConnection(
			app,
			"KafkaConnection",
			config={"bootstrap_servers": "localhost:9092"}
		)
	)

	# Pass the KafkaConnection name to KafkaTopicInitializer constructor
	kti = KafkaTopicInitializer(
		app,
		"KafkaConnection",
		config={"topics_file": "data/kafka-topic-config.yml"}
	)

	# Run the topic check step
	kti.check_and_initialize()

	# Run your app
	# app.run()
