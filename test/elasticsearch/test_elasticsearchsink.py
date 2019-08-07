from aioresponses import aioresponses

import bspump.elasticsearch
import bspump.unittest


class TestElasticSearchSink(bspump.unittest.ProcessorTestCase):

	@aioresponses()
	def test_elasticsearch_sink(self, mocked):
		mocked.post(
			"http://non-existing-url:9200/_bulk",
			body='{"items": []}',
			status=200
		)

		svc = self.App.get_service("bspump.PumpService")
		svc.add_connection(
			bspump.elasticsearch.ElasticSearchConnection(
				self.App,
				"ESConnection",
				config={
					"bulk_out_max_size": 1,
					"url": "http://non-existing-url:9200/",
				}
			)
		)

		events = [
			(None, {"hello-field": "no-important-data-here"}),
		]

		self.set_up_processor(
			bspump.elasticsearch.ElasticSearchSink,
			connection="ESConnection",
			config={
				"index_prefix": "not_existing_pattern_",
				"rollover_mechanism": "fixed",
			}
		)

		output = self.execute(
			events
		)

		expected_output_json = '{"hello-field": "no-important-data-here"}'

		request_count = 0
		for request_id, request_content in mocked.requests.items():
			request_count += 1
			url = str(request_id[1])
			assert url == "http://non-existing-url:9200/_bulk"
			assert request_content[0].kwargs["data"] == \
				'{{"index": {{ "_index": "not_existing_pattern_", "_type": "doc" }}\n{}\n'.format(expected_output_json)
		assert request_count == 1

		self.assertEqual(output, [])
