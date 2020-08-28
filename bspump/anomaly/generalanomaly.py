import asab

from ..abc.anomaly import Anomaly


class GeneralAnomaly(Anomaly):
	"""
	GeneralAnomaly serves a default anomaly class.

	Unless a specific AnomalyObject is created for a given type of the anomaly/symptom,
	GeneralAnomaly is going to be used as default.

	close_rules define how each anomaly type is closed, i. e. based on "status", or time (specify the value in seconds)
	"""

	TYPE = "default"  # N/A

	asab.Config.add_defaults(
		{
			"GeneralAnomaly": {
				"close_rules": "default:status",  # Structure: type1:rule;type2:rule ...
			},
		}
	)

	def __init__(self):
		super().__init__()

		self.CloseRules = {}
		for key_value_str in str(asab.Config["GeneralAnomaly"]["close_rules"]).split(";"):
			key_value = key_value_str.split(":")
			self.CloseRules[key_value[0]] = key_value[1]

	async def on_tick(self, current_time):
		if self["status"] == "closed":
			return

		close_rule = self.CloseRules.get(self["type"], self.CloseRules.get("default"))

		# Obtain last symptom
		last_timestamp = 0
		last_status = "open"
		for symptom in self["symptoms"]:
			timestamp = symptom.get("@timestamp")
			if timestamp > last_timestamp:
				last_timestamp = timestamp
				last_status = symptom.get("status", "open")

		if close_rule == "status" and last_status == "closed":
			self["status"] = "closed"

		if close_rule != "status":
			close_rule_seconds = int(close_rule)
			if last_timestamp != 0 and current_time > (last_timestamp + close_rule_seconds):
				self["status"] = "closed"
