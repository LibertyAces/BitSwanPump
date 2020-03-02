#!/usr/bin/env python3
import logging

import bspump.anomaly
import bspump.common
import bspump.elasticsearch
import bspump.file
import bspump.trigger

###

L = logging.getLogger(__name__)


###

"""
The following example presents a BSPump microservice, that expects symptoms of anomalies at the input,
which it assigns to anomaly objects and manages their lifecycle.

Symptom
=======

Symptoms can be either simple (f. e. user login was not successful)
or complex (f. e. logins for 80 % users were not successful during last 20 minutes).
Such symptoms should be produced by analytical microservices before they enter the pump.

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

Type of the symptom is then assigned to anomalies with the same time.
For instance, `user_login_failed` symptom is assigned to the `user_login_failed` anomaly.

Key dimensions then identify both the symptom and anomaly specifically.
For instance, key dimension for `user_login_failed` can be either a specific `user`,
or a specific ID of an `application`.

Other dimensions serve for further identification, but they do not influence
assignment to a specific anomaly.

What is the key dimension and what is not, should be defined in the configuration
(see configuration of bspump.anomaly.AnomalyAnalyzer below).

Anomaly
=======

Anomalies are composed of multiple symptoms with the same type and key dimensions.
They are opened when the first such symptom come and closed, when one of the following
strategies is configured and satisfied:

- a symptom with attribute `status` equals `closed` comes (default)
- a certain amount of time passed since the last symptom with `status` equals `open` came

The strategies are defined for every anomaly type in the configuration or specific objects (see NetworkAnomaly below).

The structure of the anomaly looks as follows:

	{
		"@timestamp": UNIX_TIMESTAMP,
		"ts_end": UNIX_TIMESTAMP,
		"type": STRING,
		"status": STRING,
		"symptoms": ARRAY,
		"key_dimension1": ...
		"key_dimension2": ...
	}

`@timestamp` is the timestamp of the first symptom.

Both open and closed anomalies are persistently stored in ElasticSearch.
When an anomaly is closed, its `_id` field in the ElasticSearch contains
the `backup` keyword.

Architecture
============

Please note the following important components:

AnomalyAnalyzer
===============

AnomalyAnalyzer analyzes symptoms of anomalies to assign them to anomalies based on key
dimensions within the symptom, which are defined in the "key_dimensions" configuration option
for every symptom type.

AnomalyManager
==============

AnomalyManager stores symptoms of anomalies to create an anomaly object based on key
dimensions within the symptom.

Dimensions are stored as part of individual symptoms inside the anomaly object.
Other dimensions than key dimensions are optional and serve only to differentiate
the symptoms from one another.

When the symptom contains status set to closed and the anomaly is specified to finish by that flag,
the anomaly "ts_end" is copied from this symptom and the anomaly object moved from "open" to "closed"
inside the anomaly storage (both in-memory and ElasticSearch, see above).

AnomalyObject
=============

AnomalyObject is created by the AnomalyManager according to the type of the anomaly.
Unless a specific AnomalyObject is created for the type, GeneralAnomaly is going to be used.

AnomalyStorage
==============

AnomalyStorage serves to store anomaly objects, separated to "open"
(anomalies that are not closed by status attribute in a symptom) and "closed".

The closed anomalies are periodically flushed from the storage to an external system.

"""


# Prepare anomaly objects


class NetworkAnomaly(bspump.Anomaly):
	"""
	Custom anomaly class for network anomalies, that manages the anomaly's lifecycle.
	"""

	TYPE = "network_down"  # This anomaly class will be used only for "network_down" anomalies

	def __init__(self):
		super().__init__()

	async def on_tick(self, current_time):
		if self["status"] == "closed":
			return

		# Close the anomaly when the status closed comes
		for symptom in self["symptoms"]:
			if symptom.get("status", "open") == "closed":
				self["status"] = "closed"


anomaly_classes = [NetworkAnomaly]


# Prepare the symptom (anomaly create) and storage (for persistence of anomalies) pipelines


class SymptomPipeline(bspump.Pipeline):
	"""
	Load the symptoms and create anomalies from them.
	"""

	def __init__(self, app, pipeline_id, anomaly_storage):
		super().__init__(app, pipeline_id)

		self.build(
			bspump.file.FileLineSource(app, self, config={
				'path': './data/anomalies.txt',
				'post': 'noop',
			}).on(bspump.trigger.OpportunisticTrigger(app)),
			bspump.common.BytesToStringParser(app, self),
			bspump.common.JsonToDictParser(app, self),
			# Map the symptom to anomalies based on their key dimensions
			bspump.anomaly.AnomalyAnalyzer(app, self, config={
				"key_dimensions": "default:user_id;network_down:server_id"
			}),
			# Manage the lifecycle of anomalies
			bspump.anomaly.AnomalyManager(app, self, anomaly_storage, anomaly_classes=anomaly_classes),
			# Print the processed symptoms to the terminal
			bspump.common.PPrintSink(app, self)
		)


class IDVersionEnricher(bspump.Generator):
	"""
	The strategy for the storage to ElasticSearch may be different for every use case.
	The following example stores the anomalies in ElasticSearch under their custom IDs
	and backups the closed ones.
	"""


	def __init__(self, app, pipeline, id=None, config=None):
		super().__init__(app, pipeline, id, config)
		self.App = app

	async def generate(self, context, event, depth):
		current_time = int(self.App.time())

		context = context["ancestor"]

		assert context.get("es_id") is not None
		context["es_version"] = current_time
		self.Pipeline.inject(context, event, depth)

		# Duplicate the event for backup
		if event.get("status") == "closed":
			context["es_version"] = "b_{}_{}".format(context["_id"], context["es_version"])
			event["backup"] = 1
			self.Pipeline.inject(context, event, depth)


class AnomalyStoragePipeline(bspump.Pipeline):
	"""
	Persist the anomalies in the ElasticSearch.
	"""

	def __init__(self, app, pipeline_id):
		super().__init__(app, pipeline_id)

		self.build(
			bspump.common.InternalSource(app, self, config={"queue_max_size": 0}),
			IDVersionEnricher(app, self),
			bspump.elasticsearch.ElasticSearchSink(app, self, "ESConnection", config={
				"index_prefix": "bs_anomaly_"
			}),
		)


# Register the storage, ES connection and pipelines and run the application


if __name__ == '__main__':
	app = bspump.BSPumpApplication()
	svc = app.get_service("bspump.PumpService")

	# Create and register all connections here

	es_connection = bspump.elasticsearch.ElasticSearchConnection(app, "ESConnection", config={
		"url": "http://localhost:9200"
	})
	svc.add_connection(es_connection)

	# Create anomaly storage

	anomaly_storage = bspump.anomaly.AnomalyStorage(app, es_connection, anomaly_classes=anomaly_classes)

	# Create and register all pipelines here

	anomaly_storage_pipeline = AnomalyStoragePipeline(app, "AnomalyStoragePipeline")
	svc.add_pipeline(anomaly_storage_pipeline)

	anomaly_pipeline = SymptomPipeline(app, "SymptomPipeline", anomaly_storage)
	svc.add_pipeline(anomaly_pipeline)

	# Run the application

	app.run()
