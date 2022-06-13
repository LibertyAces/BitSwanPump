import asyncio
import time
import confluent_kafka.admin

import bspump
import bspump.kafka
import bspump.common


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
			app, "KafkaConnection",
			config={"bootstrap_servers": "localhost:9092"}
		)
	)

	# Build example pipeline
	pipeline = bspump.Pipeline(app, "SamplePipeline")
	pipeline.build(
		bspump.kafka.KafkaSource(app, pipeline, "KafkaConnection", config={
			"topic": "test_source",
			"group_id": "test",
		}),
		bspump.common.PPrintProcessor(app, pipeline),
		bspump.kafka.KafkaSink(app, pipeline, "KafkaConnection", config={
			"topic": "test_sink"
		}),
	)
	svc.add_pipeline(pipeline)

	# Pass the KafkaConnection name to KafkaTopicInitializer constructor
	kti = bspump.kafka.KafkaTopicInitializer(app, "KafkaConnection")

	# Add topics required by pipeline components
	kti.include_topics(pipeline=pipeline)

	# Add topics from YAML file
	kti.include_topics(config_file="data/kafka-topic-config.yml")

	# Add topics from dict config
	kti.include_topics(topic_config={
		"topic": "new_topic",
		"num_partitions": 1,
		"replication_factor": 1,
		"retention.ms": 3600000,
	})

	# Check and create missing topics
	kti.initialize_topics()

	# Run your app
	# app.run()
