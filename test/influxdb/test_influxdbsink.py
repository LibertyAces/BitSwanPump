from aioresponses import aioresponses

import bspump.unittest
from bspump.influxdb import InfluxDBConnection, InfluxDBSink


class TestInfluxDBSink(bspump.unittest.ProcessorTestCase):

	@aioresponses()
	def test_influxdb_sink(self, mocked):
		mocked.post(
			"http://test:8086/write?db=test",
			status=204
		)

		svc = self.App.get_service("bspump.PumpService")
		svc.add_connection(
			InfluxDBConnection(
				self.App,
				"InfluxDBConnection",
				config={
					"output_bucket_max_size": "1",
					"url": "http://test:8086/",
					"db": "test",
				}
			)
		)

		events = [
			(None, ("collection", "tag1=a,tag2=b", "field=12", 1234567890)),
		]

		self.set_up_processor(
			InfluxDBSink,
			connection="InfluxDBConnection"
		)

		output = self.execute(
			events
		)

		requests = mocked.requests.items()
		self.assertEqual(1, len(requests))
		request = next(iter(requests))
		self.assertEqual("http://test:8086/write?db=test", str(request[0][1]))
		self.assertEqual("collection,tag1=a,tag2=b field=12 1234567890000000000", request[1][0][1]["data"].strip())

		self.assertEqual(output, [])
