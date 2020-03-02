from ..abc.processor import Processor

from .generalanomaly import GeneralAnomaly


class AnomalyManager(Processor):
	"""
	AnomalyManager stores symptoms of anomalies to create an anomaly object based on key
	dimensions within the symptom

	Dimensions are stored as part of individual symptoms inside the anomaly object.
	Other dimensions than key dimensions are optional and serve only to differentiate
	the symptoms from one another.

	The final anomaly objects, which can be obtained from the AnomalyStorage, then contain
	the following fields (where @timestamp is the timestamp of the first symptom):

	{
		"@timestamp": UNIX_TIMESTAMP,
		"ts_end": UNIX_TIMESTAMP,
		"type": STRING,
		"status": STRING,
		"symptoms": ARRAY,
		"key_dimension1": ...
		"key_dimension2": ...
	}

	When the symptom contains status set to closed and the anomaly is specified to finish by that flag,
	the anomaly "ts_end" is copied from this symptom and the anomaly object moved from "open" to "closed"
	inside the anomaly storage.
	"""

	def __init__(self, app, pipeline, anomaly_storage, anomaly_classes=list(), id=None, config=None):
		super().__init__(app, pipeline, id, config)

		self.AnomalyStorage = anomaly_storage
		self.AnomalyClasses = anomaly_classes

		metrics_service = app.get_service('asab.MetricsService')
		self.AnomalyManagerCounter = metrics_service.create_counter(
			"anomaly.manager",
			init_values={
				"timestamp.miss": 0,
				"key.miss": 0,
				"key.dimensions.miss": 0,
				"type.miss": 0,
				"symptom.miss": 0,
			}
		)

	def create_anomaly(self, key_dimensions, timestamp_started, anomaly_type):
		selected_anomaly_class = GeneralAnomaly
		for anomaly_class in self.AnomalyClasses:
			if anomaly_class.TYPE == anomaly_type:
				selected_anomaly_class = anomaly_class
				break

		anomaly = selected_anomaly_class()
		anomaly["@timestamp"] = timestamp_started
		anomaly["type"] = anomaly_type
		anomaly["status"] = "open"
		anomaly["symptoms"] = []

		# Store all key dimensions in top level
		for dim_name, dim_value in key_dimensions.items():
			anomaly[dim_name] = dim_value

		return anomaly

	def process(self, context, event):
		# Obtain timestamp
		timestamp = event.get("@timestamp")
		if timestamp is None:
			self.AnomalyManagerCounter.add("timestamp.miss", 1)
			return None

		# Obtain key
		key = event.get("key")
		if key is None:
			self.AnomalyManagerCounter.add("key.miss", 1)
			return None

		# Obtain key dimensions
		key_dimensions = event.get("key_dimensions")
		if key_dimensions is None:
			self.AnomalyManagerCounter.add("key.dimensions.miss", 1)
			return None

		# Obtain type
		anomaly_type = event.get("type")
		if anomaly_type is None:
			self.AnomalyManagerCounter.add("type.miss", 1)
			return None

		# Obtain symptom data
		symptom = event.get("symptom")
		if symptom is None:
			self.AnomalyManagerCounter.add("symptom.miss", 1)
			return None

		# Store the open anomaly in the storage
		if key not in self.AnomalyStorage["open"]:
			anomaly = self.create_anomaly(key_dimensions, timestamp, anomaly_type)
			self.AnomalyStorage["open"][key] = anomaly

		# Append symptom to the anomaly
		self.AnomalyStorage["open"][key]["symptoms"].append(symptom)

		return event
