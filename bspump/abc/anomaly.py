class Anomaly(dict):
	"""
	Description: 	Anomaly is an abstract class to be overriden for a specific anomaly and its type.

	:return:

	Implement: TYPE, on_tick
	"""

	TYPE = None

	def is_closed(self):
		"""
		Description:

		:return:
		"""
		return self.get("status") == "closed"

	def close(self, current_time):
		"""
		Description:

		:return:
		"""
		self["ts_end"] = current_time
		self["D"] = self["ts_end"] - self["@timestamp"]
		self["status"] = "closed"

	async def on_tick(self, current_time):
		"""
		Description:

		:return:

		:hint: Implement to perform operations on the anomaly, f. e. close.
		"""
		raise NotImplementedError()
