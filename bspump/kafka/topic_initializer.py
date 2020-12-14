import logging
import re
import typing

import kafka.admin

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
		# Topics syntax: <topic_name>[:<num_partitions>:<replication_factor>]
		# If the optional values are not specified, they fall back to their default values
		# Multiple entries are allowed, separated by whitespace
		# Example:
		#    cool_topic  great_topic:1:2  neat_topic::3
		"topics": "example_topic",
		"num_partitions": 1,
		"replication_factor": 1,
	}

	def __init__(self, app, connection, id: typing.Optional[str] = None, config: dict = None):
		_id = id if id is not None else self.__class__.__name__
		super().__init__(_id, config)
		self.App = app
		self.AdminClient = None

		self.bootstrap_servers = self.get_bootstrap_servers(connection)
		self.client_id = self.Config["client_id"]
		self.num_partitions_default = self.Config["num_partitions"]
		self.replication_factor_default = self.Config["replication_factor"]
		self.required_topics = self.parse_topics_config(self.Config["topics"])

	def get_bootstrap_servers(self, connection):
		return re.split(r"[\s,]+", self.App.BSPumpService.Connections[connection].Config["bootstrap_servers"])

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
		L.debug(f"Parsing topics string: {config_str}")
		required_topics = []
		for topic_entry in re.split(r"\s+", config_str):
			topic = {}
			settings = topic_entry.split(":")
			if len(settings) == 1:
				topic["name"] = settings[0]
				topic["num_partitions"] = int(self.num_partitions_default)
				topic["replication_factor"] = int(self.replication_factor_default)
			elif len(settings) == 3:
				topic["name"] = settings[0]
				if settings[1]:
					topic["num_partitions"] = int(settings[1])
				else:
					topic["num_partitions"] = int(self.num_partitions_default)
				if settings[2]:
					topic["replication_factor"] = int(settings[2])
				else:
					topic["replication_factor"] = int(self.replication_factor_default)
			else:
				raise ValueError(f"Got '{topic_entry}', expected 'topic_name[:num_partitions:replication_factor]'")
			required_topics.append(topic)
		return required_topics

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
		self.open_connection()
		try:
			missing_topics = self.get_missing_topics()
			if missing_topics:
				self.create_topics(missing_topics)
			else:
				L.debug("All topics are initialized already.")
		finally:
			if self.AdminClient:
				self.close_connection()
