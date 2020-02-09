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
				"rollover_mechanism": "noop",
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
			self.assertEqual("http://non-existing-url:9200/_bulk", url)
			self.assertEqual(
				'{{"index": {{"_index": "not_existing_pattern_", "_type": "doc"}}}}\n{{"doc": {}}}\n'.format(
					expected_output_json),
				request_content[0].kwargs["data"]
			)
		self.assertEqual(1, request_count)

		self.assertEqual(output, [])

	@aioresponses()
	def test_elasticsearch_sink_upsert(self, mocked):
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
			(
				{
					"elasticsearch_operation_metadata": {"_id": "my_id", "_index": "override_index"},
					"elasticsearch_doc_metadata": {"doc_as_upsert": True}
				},
				{"hello-field": "no-important-data-here"}
			)
		]

		self.set_up_processor(
			bspump.elasticsearch.ElasticSearchSink,
			connection="ESConnection",
			config={
				"index_prefix": "not_existing_pattern_",
				"rollover_mechanism": "noop",
			}
		)

		output = self.execute(
			events
		)

		request_count = 0
		for request_id, request_content in mocked.requests.items():
			request_count += 1
			url = str(request_id[1])
			self.assertEqual("http://non-existing-url:9200/_bulk", url)
			self.assertEqual(
				'{"index": {"_index": "override_index", "_type": "doc", "_id": "my_id"}}\n'
				'{"doc": {"hello-field": "no-important-data-here"}, "doc_as_upsert": true}\n',
				request_content[0].kwargs["data"]
			)
		self.assertEqual(1, request_count)

		self.assertEqual(output, [])
