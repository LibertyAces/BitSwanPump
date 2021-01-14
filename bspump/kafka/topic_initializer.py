import json
import logging
import re
import typing

import kafka.admin
import yaml

from asab import ConfigObject

#

L = logging.getLogger(__name__)


#


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
	KafkaTopicInitializer("KafkaTopicInitializer").check_and_initialize()
	"""

	ConfigDefaults = {
		"client_id": "bspump-topic-initializer",
		"topics_file": "",
		# Topics syntax: <topic_name>[:<num_partitions>:<replication_factor>]
		# If the optional values are not specified, they fall back to their default values
		# Multiple entries are allowed, separated by whitespace
		# Example:
		#    cool_topic  great_topic:1:2  neat_topic::3
		"topics": "",
		"num_partitions": 1,
		"replication_factor": 1,
	}

	def __init__(self, app, connection, id: typing.Optional[str] = None, config: dict = None):
		_id = id if id is not None else self.__class__.__name__
		super().__init__(_id, config)
		self.AdminClient = None

		self.get_bootstrap_servers(app, connection)
		self.client_id = self.Config.get("client_id")

		self.required_topics = []
		self.parse_topics_config(self.Config["topics"])
		topics_file = self.Config.get("topics_file")
		if len(topics_file) != 0:
			self.load_topics_from_file(topics_file)

	def get_bootstrap_servers(self, app, connection):
		svc = app.get_service("bspump.PumpService")
		self.bootstrap_servers = re.split(r"[\s,]+", svc.Connections[connection].Config["bootstrap_servers"].strip())

	def open_connection(self):
		try:
			L.debug("Opening KafkaAdminClient connection...")
			self.AdminClient = kafka.admin.KafkaAdminClient(
				bootstrap_servers=self.bootstrap_servers,
				client_id=self.client_id)
			L.debug("Connected to '{}' as '{}'".format(self.bootstrap_servers, self.client_id))
		except Exception as e:
			L.error("Cannot connect to '{}'".format(self.bootstrap_servers))
			raise e

	def close_connection(self):
		if self.AdminClient:
			self.AdminClient.close()
			L.debug("KafkaAdminClient connection closed.")
		else:
			L.warning("No open KafkaAdminClient connection.")

	def parse_topics_config(self, config_str: str) -> typing.Optional[typing.List[dict]]:
		if not config_str.strip():
			L.info("Topics string is empty")
			return
		num_partitions_default = self.Config.get("num_partitions")
		replication_factor_default = self.Config.get("replication_factor")
		L.debug(f"Parsing topics string: {config_str}")
		for topic_entry in re.split(r"\s+", config_str):
			topic = {}
			settings = topic_entry.split(":")
			if len(settings) == 1:
				topic["name"] = settings[0]
				topic["num_partitions"] = int(num_partitions_default)
				topic["replication_factor"] = int(replication_factor_default)
			elif len(settings) == 3:
				topic["name"] = settings[0]
				if settings[1]:
					topic["num_partitions"] = int(settings[1])
				else:
					topic["num_partitions"] = int(num_partitions_default)
				if settings[2]:
					topic["replication_factor"] = int(settings[2])
				else:
					topic["replication_factor"] = int(replication_factor_default)
			else:
				raise ValueError(f"Got '{topic_entry}', expected 'topic_name[:num_partitions:replication_factor]'")
			self.required_topics.append(topic)

	def load_topics_from_file(self, topics_file: str):
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
					L.warning("Topic is missing mandatory field '{}'. Skipping.".format(field))
					break
			else:
				self.required_topics.append(topic)

	def get_missing_topics(self) -> typing.List[dict]:
		L.debug("Retrieving list of existing topics...")
		existing_topics = self.AdminClient.list_topics()
		missing_topics = [
			topic
			for topic in self.required_topics
			if topic["name"] not in existing_topics
		]
		return missing_topics

	def create_topics(self, topics: typing.Iterable[dict]):
		L.debug("Creating topics...")
		topics_to_create = [
			kafka.admin.NewTopic(**topic) for topic in topics]
		self.AdminClient.create_topics(topics_to_create)
		L.info("Missing topics created: {}".format(" ".join([topic["name"] for topic in topics])))

	def check_and_initialize(self):
		if not self.required_topics:
			L.info("No topics specified.")
			return
		try:
			self.open_connection()
			missing_topics = self.get_missing_topics()
			if missing_topics:
				self.create_topics(missing_topics)
			else:
				L.debug("All topics are initialized already.")
		finally:
			if self.AdminClient:
				self.close_connection()
