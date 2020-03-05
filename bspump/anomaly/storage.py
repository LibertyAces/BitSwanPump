import time
import logging
import collections

import asyncio

import asab

from .generalanomaly import GeneralAnomaly

###

L = logging.getLogger(__name__)

###


class AnomalyStorage(asab.ConfigObject, collections.OrderedDict):
	"""
	AnomalyStorage serves to store anomaly objects (see AnomalyManager for details),
	separated to "open" (anomalies that are not closed by status attribute in a symptom) and "closed".

	The closed anomalies are periodically flushed from the storage to an external system.
	"""

	ConfigDefaults = {
		"closed_anomaly_longevity": 5,  # Anomalies come pretty often
		"index": "bs_anomaly*",
	}

	def __init__(self, app, es_connection, anomaly_classes=list(), anomaly_storage_pipeline_source="AnomalyStoragePipeline.*InternalSource", pipeline=None, id="AnomalyStorage", config=None):
		super().__init__(config_section_name=id, config=config)

		self["open"] = {}
		self["closed"] = {}

		self.App = app
		self.Id = id
		self.Pipeline = pipeline
		self.AnomalyStoragePipelineSource = anomaly_storage_pipeline_source
		self.Context = {}
		self.AnomalyClasses = anomaly_classes
		self.ClosedAnomalyLongevity = int(self.Config["closed_anomaly_longevity"])
		self.Index = str(self.Config["index"])
		self.Connection = es_connection

		# Subscribe to periodically flush old closed anomalies
		self.App.PubSub.subscribe("Application.tick/300!", self.flush)

		metrics_service = self.App.get_service('asab.MetricsService')
		self.AnomalyStorageCounter = metrics_service.create_counter(
			"anomaly.storage",
			init_values={
				"anomalies.closed.flushed": 0,
				"anomalies.open.flushed": 0,
			}
		)

		# Load previously saved anomalies from the external system
		self.LoadTasks = [asyncio.ensure_future(self.load(), loop=self.App.Loop)]
		self.App.PubSub.subscribe("Application.exit!", self._on_exit)

	def set_pipeline(self, pipeline):
		self.Pipeline = pipeline

	async def load(self):
		query = {
			"size": 10000,
			"query": {
				"bool": {
					"must": [
						{
							"exists": {
								"field": "@timestamp"
							},
						},
						{
							"exists": {
								"field": "type"
							},
						},
						{
							"exists": {
								"field": "status"
							},
						},
						{
							"match": {
								"status": {
									"query": "open",
									"minimum_should_match": 1,
									"zero_terms_query": "all"
								}
							}
						},
						{
							"range": {
								"@timestamp": {
									"gte": "now-14d",
									"lte": "now"
								},
							},
						},
					]
				}
			},
			"sort": [
				{"@timestamp": {"order": "asc"}}
			]
		}

		url = self.Connection.get_url() + '{}/_search'.format(self.Index)
		async with self.Connection.get_session() as session:
			async with session.post(
				url,
				json=query,
				headers={'Content-Type': 'application/json'}
			) as response:
				if response.status != 200:
					data = await response.text()
					L.error("Failed to fetch data from ElasticSearch: {} from {}\n{}".format(response.status, url, data))
					return
				msg = await response.json()

		hits = msg["hits"]["hits"]
		if len(hits) == 0:
			L.warning("No open anomalies present in ElasticSearch ...")
			return

		# Save open/future anomalies to the in-memory dictionary
		for hit in hits:
			key = hit['_id']
			# Prevent backups
			if not key.startswith("b_"):
				event = hit['_source']
				# Modify timestamp
				event["@timestamp"] = int(event["@timestamp"] / 1000)
				# Select proper anomaly class
				selected_anomaly_class = GeneralAnomaly
				for anomaly_class in self.AnomalyClasses:
					if anomaly_class.TYPE == event["type"]:
						selected_anomaly_class = anomaly_class
						break
				# Add all data
				anomaly = selected_anomaly_class()
				for a_key, a_value in event.items():
					anomaly[a_key] = a_value
				# Save the anomaly
				self["open"][key] = anomaly

		L.info("Open anomalies loaded ...")

	async def _on_exit(self, message_type):
		await asyncio.wait(self.LoadTasks, loop=self.App.Loop)

	async def flush(self, message_type):
		L.info("Start flushing of closed anomalies ...")

		current_time = int(time.time())

		# Throttle the parental pipeline
		if self.Pipeline is not None:
			self.Pipeline.throttle(self.Id, True)

		svc = self.App.get_service("bspump.PumpService")
		anomaly_storage_pipeline_source = svc.locate(self.AnomalyStoragePipelineSource)

		if anomaly_storage_pipeline_source is None:
			L.warning("The anomaly storage pipeline is not yet ready, skipping ...")
			return

		keys_to_be_deleted = []

		# Update anomalies & close them, if it is possible
		for key, anomaly in self["open"].items():
			await anomaly.on_tick(current_time)
			if anomaly["status"] == "closed":
				anomaly.close(current_time)
				self["closed"][key] = anomaly
				keys_to_be_deleted.append(key)

		# Remove moved anomalies from the storage
		for key in keys_to_be_deleted:
			del self["open"][key]

		keys_to_be_deleted = []

		# FLUSH old closed anomalies to external database
		await asyncio.sleep(0.01)
		# Synchronous to make atomic cycle
		for key, anomaly in self["closed"].items():
			if current_time > anomaly["ts_end"] + self.ClosedAnomalyLongevity:
				# Pass anomaly to the storage pipeline
				self.Context["es_id"] = key
				await anomaly_storage_pipeline_source.put_async(self.Context, anomaly)
				self.AnomalyStorageCounter.add("anomalies.closed.flushed", 1)
				keys_to_be_deleted.append(key)

		# Remove old closed anomalies from the storage
		for key in keys_to_be_deleted:
			del self["closed"][key]

		# FLUSH open anomalies for persistence to external system
		await asyncio.sleep(0.01)
		# Synchronous to make atomic cycle
		for key, anomaly in self["open"].items():
			self.Context["es_id"] = key
			await anomaly_storage_pipeline_source.put_async(self.Context, anomaly)
			self.AnomalyStorageCounter.add("anomalies.open.flushed", 1)

		# Throttle the parental pipeline
		if self.Pipeline is not None:
			self.Pipeline.throttle(self.Id, False)

		L.info("End flushing of closed anomalies ...")
