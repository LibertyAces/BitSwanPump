#!/usr/bin/env python3
import bspump
import bspump.common
import bspump.clickhouse
import bspump.random
import bspump.trigger


class PrintSink(bspump.Sink):

	def process(self, context, event):
		print("RECEIVED: ", context, event)


class ClickHouseSinkPipeline(bspump.Pipeline):

	def __init__(self, app, pipeline_id):
		super().__init__(app, pipeline_id)
		self.build(
			bspump.random.RandomSource(
				app,
				self,
				choice=[
					{"@timestamp": 100, "log.original": "test1"},
					{"@timestamp": 200, "log.original": "test2"},
				],
				config={
					'number': 2
				}
			).on(bspump.trigger.OpportunisticTrigger(app, chilldown_period=10)),

			bspump.clickhouse.ClickHouseSink(app, self, "ClickHouseConnection", config={
				'host': 'localhost',
				'database': 'bspump',
				'table': 'logs',
				'schema': '`@timestamp` Int64, `log.original` String',
				'bulk_size': 2,
			}),
		)


class ClickHouseSourcePipeline(bspump.Pipeline):

	def __init__(self, app, pipeline_id):
		super().__init__(app, pipeline_id)
		self.build(
			bspump.clickhouse.ClickHouseSource(app, self, "ClickHouseConnection", config={
				'host': 'localhost',
				'database': 'bspump',
				'table': 'logs',
			}),

			PrintSink(app, self),
		)


if __name__ == '__main__':
	app = bspump.BSPumpApplication()

	svc = app.get_service("bspump.PumpService")

	svc.add_connection(
		bspump.clickhouse.ClickHouseConnection(app, "ClickHouse", config={
		})
	)

	svc.add_pipeline(
		ClickHouseSinkPipeline(app, "ClickHouseSinkPipeline")
	)
	svc.add_pipeline(
		ClickHouseSourcePipeline(app, "ClickHouseSourcePipeline")
	)

	app.run()
