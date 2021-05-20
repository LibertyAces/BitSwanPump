import json
import logging
import re
import typing

import asab
import kafka.admin
import yaml

from asab import ConfigObject

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


class KafkaTopicInitializer(ConfigObject):
	"""
	KafkaTopicInitializer purpose:
	- get bootstrap_servers from app.BSPumpService.
	- connect to Kafka server using kafka.KafkaAdminClient
	- check if required topics exist
	- if not, create them

	KafkaAdminClient requires blocking connection, which is why this class doesn't use
	the connection module from BSPump.

	Usage:
	topic_initializer = KafkaTopicInitializer(app, "KafkaConnection")
	topic_initializer.extract_topics("pipeline:EnrichersPipeline:KafkaSink")
	topic_initializer.extract_topics("pipeline:EnrichersPipeline:KafkaSource")
	topic_initializer.run()
	"""

	ConfigDefaults = {
		"client_id": "bspump-topic-initializer",
		"topics_file": "",
		"num_partitions_default": 2,
		"replication_factor_default": 3,
	}

	def __init__(self, app, connection, id: typing.Optional[str] = None, config: dict = None):
		_id = id if id is not None else self.__class__.__name__
		super().__init__(_id, config)

		self.required_topics = []
		self.bootstrap_servers = None
		self.client_id = self.Config.get("client_id")

		self._get_bootstrap_servers(app, connection)

		topics_file = self.Config.get("topics_file")
		if len(topics_file) != 0:
			self.load_topics_from_file(topics_file)

	def _get_bootstrap_servers(self, app, connection):
		svc = app.get_service("bspump.PumpService")
		self.bootstrap_servers = re.split(r"[\s,]+", svc.Connections[connection].Config["bootstrap_servers"].strip())

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
				self.required_topics.append(topic)

	def extract_topics(self, topic_section):
		# Every kafka topic needs to have: name, num_partitions and replication_factor
		topic_names = asab.Config.get("topic").split(",")
		num_partitions = asab.Config.get(
			"num_partitions",
			self.Config.get("num_partitions_default")
		)
		replication_factor = asab.Config.get(
			"replication_factor",
			self.Config.get("replication_factor_default")
		)

		# Additional configs are optional
		topic_configs = {}
		for config_option in asab.Config.options(topic_section):
			if config_option in _TOPIC_CONFIG_OPTIONS:
				topic_configs[config_option] = asab.Config.get(config_option)

		# Create topic objects
		for name in topic_names:
			self.required_topics.append(kafka.admin.NewTopic(
				name,
				num_partitions,
				replication_factor,
				topic_configs=topic_configs
			))

	def check_and_initialize(self):
		try:
			admin_client = kafka.admin.KafkaAdminClient(
				bootstrap_servers=self.bootstrap_servers,
				client_id=self.client_id
			)

			# Filter out the topics that already exist
			existing_topics = admin_client.list_topics()
			missing_topics = [
				topic
				for topic in self.required_topics
				if topic.name not in existing_topics
			]

			# Create topics
			# TODO: update configs of existing topics using `admin_client.alter_configs()`
			admin_client.create_topics(missing_topics)
			L.log(
				asab.LOG_NOTICE,
				"Kafka topics created",
				struct_data=[topic.name for topic in missing_topics]
			)
		except Exception as e:
			L.error("Kafka topic initialization failed: {}".format(e))
		finally:
			if admin_client is not None:
				admin_client.close()
