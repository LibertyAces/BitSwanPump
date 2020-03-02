from ..abc.generator import Generator


class AnomalyAnalyzer(Generator):
	"""
	AnomalyAnalyzer analyzes symptoms of anomalies to assign them to anomalies based on key
	dimensions within the symptom, which are defined in the "key_dimensions" configuration option
	for every symptom type.

	Every symptom should contain the following fields:
	{
		"@timestamp": UNIX_TIMESTAMP,
		"type": STRING,
		"key_dimension1": ...
		"key_dimension2": ...
		...
		"other_dimension": ... (OPTIONAL)
		...
		"status": future/open/closed (OPTIONAL)
	}
	"""

	ConfigDefaults = {
		"key_dimensions": "default:user_id",  # Structure: type1:key_dimension1,key_dimension2;type2:key_dimension1 ...
	}

	def __init__(self, app, pipeline, id=None, config=None):
		super().__init__(app, pipeline, id, config)

		self.KeyDimensions = {}
		for key_value_str in self.Config["key_dimensions"].split(";"):
			key_value = key_value_str.split(":")
			self.KeyDimensions[key_value[0]] = key_value[1].split(",")

		metrics_service = app.get_service('asab.MetricsService')
		self.AnomalyAnalyzerCounter = metrics_service.create_counter(
			"anomaly.analyzer",
			init_values={
				"timestamp.miss": 0,
				"key.dimensions.miss": 0,
			}
		)

	def _construct_key(self, event, out_dimensions=None):
		key = ""

		# Obtain list of key dimensions that should be part of the event / symptom
		symptom_type = event.get("type", "")
		key_dimensions = self.KeyDimensions.get(symptom_type)
		if key_dimensions is None:
			key_dimensions = self.KeyDimensions.get("default")

		# Construct the key based on key dimensions
		for key_dimension in key_dimensions:
			if len(key_dimension) == 0:
				continue
			value = event.get(key_dimension)
			if value is None:
				continue
			key += str(value)
			if out_dimensions is not None:
				out_dimensions[key_dimension] = value

		if len(key) < 1:
			return None

		key += symptom_type

		return key

	async def generate(self, context, event, depth):
		# Obtain timestamp
		timestamp = event.get("@timestamp")
		if timestamp is None:
			self.AnomalyAnalyzerCounter.add("timestamp.miss", 1)
			return None

		if isinstance(timestamp, str):
			return None

		# Construct unique key for the anomaly
		key_dimensions = {}
		key = self._construct_key(event, key_dimensions)
		if key is None:
			self.AnomalyAnalyzerCounter.add("key.dimensions.miss", 1)
			return None

		# Pass the symptom to anomaly manager and its anomaly factory function
		# So far, the mapping is 1:1, i. e. one symptom type is associated with one anomaly type
		self.Pipeline.inject(context, {
			"@timestamp": timestamp,
			"key": key,
			"key_dimensions": key_dimensions,
			"type": event.get("type"),
			"symptom": event,
		}, depth)
