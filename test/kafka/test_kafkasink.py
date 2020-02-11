from unittest.mock import patch

import bspump.unittest
from bspump.kafka import KafkaConnection, KafkaSink


class TestKafkaSink(bspump.unittest.ProcessorTestCase):

	@patch("bspump.kafka.sink.KafkaSink._on_health_check", lambda *x: None)
	def test_producer_params_configuration(self):

		svc = self.App.get_service("bspump.PumpService")
		svc.add_connection(
			KafkaConnection(
				self.App,
				"KafkaConnection",
				config={
					"bootstrap_servers": "kafka:9092"
				}
			)
		)

		self.set_up_processor(
			KafkaSink,
			connection="KafkaConnection",
			config={
				"client_id": "a",
				"metadata_max_age_ms": "1",
				"request_timeout_ms": "2",
				"api_version": "2.9.0",
				"max_batch_size": "3",
				"max_request_size": "4",
				"linger_ms": "5",
				"send_backoff_ms": "6",
				"retry_backoff_ms": "7",
				"connections_max_idle_ms": "8",
				"enable_idempotence": "True",
				"transactional_id": "c",
				"transaction_timeout_ms": "9",
				"acks": "all"
			}
		)

		output = self.execute([(None, {})])
		self.assertEqual(output, [])

		self.assert_config_value("client_id", "a")
		self.assert_config_value("metadata_max_age_ms", 1)
		self.assert_config_value("request_timeout_ms", 2)
		self.assert_config_value("api_version", "2.9.0")
		self.assert_config_value("max_batch_size", 3)
		self.assert_config_value("max_request_size", 4)
		self.assert_config_value("linger_ms", 5)
		self.assert_config_value("send_backoff_ms", 6)
		self.assert_config_value("retry_backoff_ms", 7)
		self.assert_config_value("connections_max_idle_ms", 8)
		self.assert_config_value("enable_idempotence", True)
		self.assert_config_value("transactional_id", "c")
		self.assert_config_value("transaction_timeout_ms", 9)
		self.assert_config_value("acks", "all")

	def assert_config_value(self, key, value):
		self.assertEqual(value, self.Pipeline.Processor._producer_params.get(key))
