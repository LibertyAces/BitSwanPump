import json
import yaml
import logging
import re
import typing

import kafka.admin

import asab
import bspump
import bspump.abc.sink
import bspump.abc.source

try:
    import fastkafka
except ImportError:
    fastkafka = None


#

L = logging.getLogger(__name__)

#

_TOPIC_CONFIG_OPTIONS = {
	'compression.type',
	'leader.replication.throttled.replicas',
	'message.downconversion.enable',
	'min.insync.replicas',
	'segment.jitter.ms',
	'cleanup.policy',
	'flush.ms',
	'follower.replication.throttled.replicas',
	'segment.bytes',
	'retention.ms',
	'flush.messages',
	'message.format.version',
	'max.compaction.lag.ms',
	'file.delete.delay.ms',
	'max.message.bytes',
	'min.compaction.lag.ms',
	'message.timestamp.type',
	'preallocate',
	'min.cleanable.dirty.ratio',
	'index.interval.bytes',
	'unclean.leader.election.enable',
	'retention.bytes',
	'delete.retention.ms',
	'segment.ms',
	'message.timestamp.difference.max.ms',
	'segment.index.bytes'
}


def _is_kafka_component(component):
	if isinstance(component, bspump.kafka.KafkaSource) \
		   or isinstance(component, bspump.kafka.KafkaSink):
		return True
	if fastkafka is not None:
		return isinstance(component, fastkafka.FastKafkaSource) \
			   or isinstance(component, fastkafka.FastKafkaSink)
	return False


class KafkaTopicInitializer(asab.ConfigObject):
	"""
	KafkaTopicInitializer reads topic configs from file or from Kafka sink/source configs,
	checks if they exists and creates them if they don't.

	KafkaAdminClient requires blocking connection, which is why this class doesn't use
	the connection module from BSPump.

	Usage:
	topic_initializer = KafkaTopicInitializer(app, "KafkaConnection")
	topic_initializer.include_topics(MyPipeline)
	topic_initializer.run()
	"""

	ConfigDefaults = {
		"client_id": "bspump-topic-initializer",
		"topics_file": "",
		"num_partitions_default": 1,
		"replication_factor_default": 1,
	}

	def __init__(self, app, connection, id: typing.Optional[str] = None, config: dict = None):
		_id = id if id is not None else self.__class__.__name__
		super().__init__(_id, config)

		self.RequiredTopics = []
		self.BootstrapServers = None
		self.ClientId = self.Config.get("client_id")

		self._get_bootstrap_servers(app, connection)

		topics_file = self.Config.get("topics_file")
		if len(topics_file) != 0:
			self.load_topics_from_file(topics_file)

	def _get_bootstrap_servers(self, app, connection):
		svc = app.get_service("bspump.PumpService")
		self.BootstrapServers = re.split(r"[\s,]+", svc.Connections[connection].Config["bootstrap_servers"].strip())

	def load_topics_from_file(self, topics_file: str):
		# Support yaml and json input
		ext = topics_file.strip().split(".")[-1].lower()
		if ext == "json":
			with open(topics_file, "r") as f:
				data = json.load(f)
		elif ext in ("yml", "yaml"):
			with open(topics_file, "r") as f:
				data = yaml.safe_load(f)
		else:
			L.warning("Unsupported extension: '{}'".format(ext))

		for topic in data:
			for field in ("name", "num_partitions", "replication_factor"):
				if field not in topic:
					L.warning("Topic declaration is missing mandatory field '{}'. Skipping.".format(field))
					break
			else:
				self.RequiredTopics.append(topic)

	def include_topics(self, bspump_component):
		# Get topics from Kafka Source or Sink
		if _is_kafka_component(bspump_component):
			L.info("Including topics from {}".format(bspump_component.Id))
			self.include_topics_from_config(bspump_component.Config)
			return

		# Scan the pipeline for KafkaSource(s) or KafkaSink
		if isinstance(bspump_component, bspump.Pipeline):
			for source in bspump_component.Sources:
				if _is_kafka_component(source):
					L.info("Including topics from {}".format(source.Id))
					self.include_topics_from_config(source.Config)
			sink = bspump_component.Processors[-1]
			if _is_kafka_component(sink):
				L.info("Including topics from {}".format(sink.Id))
				self.include_topics_from_config(sink.Config)
			return

		L.error("Unsupported topic source: {}".format(bspump_component.__class__))

	def include_topics_from_config(self, config_object):
		# Every kafka topic needs to have: name, num_partitions and replication_factor
		topic_names = config_object.get("topic").split(",")

		if "num_partitions" in config_object:
			num_partitions = int(config_object.pop("num_partitions"))
		else:
			num_partitions = int(self.Config.get("num_partitions_default"))

		if "replication_factor" in config_object:
			replication_factor = int(config_object.pop("replication_factor"))
		else:
			replication_factor = int(self.Config.get("replication_factor_default"))

		# Additional configs are optional
		topic_configs = {}
		for config_option in config_object:
			if config_option in _TOPIC_CONFIG_OPTIONS:
				topic_configs[config_option] = config_object.pop(config_option)

		# Create topic objects
		for name in topic_names:
			self.RequiredTopics.append(kafka.admin.NewTopic(
				name,
				num_partitions,
				replication_factor,
				topic_configs=topic_configs
			))

	def check_and_initialize(self):
		L.warning("`check_and_initialize()` is obsoleted, use `run()` instead")

	def run(self):
		admin_client = None
		try:
			admin_client = kafka.admin.KafkaAdminClient(
				bootstrap_servers=self.BootstrapServers,
				client_id=self.ClientId
			)

			# Filter out the topics that already exist
			existing_topics = admin_client.list_topics()
			missing_topics = [
				topic
				for topic in self.RequiredTopics
				if topic.name not in existing_topics
			]

			# Create topics
			# TODO: update configs of existing topics using `admin_client.alter_configs()`
			admin_client.create_topics(missing_topics)
			L.log(
				asab.LOG_NOTICE,
				"Kafka topics created",
				struct_data={"topics": [topic.name for topic in missing_topics]}
			)
		except Exception as e:
			L.error("Kafka topic initialization failed: {}".format(e))
		finally:
			if admin_client is not None:
				admin_client.close()
