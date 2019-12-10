import logging

import bspump
import bspump.common
import bspump.file
import bspump.lookup
import bspump.trigger

###

L = logging.getLogger(__name__)

###


class MyApplication(bspump.BSPumpApplication):
	def __init__(self):
		super().__init__()

		svc = self.get_service("bspump.PumpService")
		self.IPGeoLookup = bspump.lookup.IPGeoLookup(self, "IPGeoLookup", config={
			"path": "./data/ip_address_source.csv",
		})
		svc.add_lookup(self.IPGeoLookup)

		svc.add_pipeline(MyPipeline(self))
		

class MyPipeline(bspump.Pipeline):

	def __init__(self, app, pipeline_id=None):
		super().__init__(app, pipeline_id)
		self.build(
			bspump.file.FileCSVSource(app, self, config={
				"path": "./data/ip_addresses.csv",
				"post": "noop",
			}).on(bspump.trigger.OpportunisticTrigger(app)),
			# Chose IPv4 or IPv6 processor
			MyProcessorIPV4(app, self),
			# MyProcessorIPV6(app, self),
			bspump.common.PPrintSink(app, self)
		)


class MyProcessorIPV4(bspump.Processor):

	def __init__(self, app, pipeline, id=None, config=None):
		super().__init__(app, pipeline, id, config)
		svc = app.get_service("bspump.PumpService")
		self.Lookup = svc.locate_lookup("IPGeoLookup")
		self.Lookup.PubSub.subscribe("bspump.Lookup.changed!", self.on_ip_geo_lookup_changed)


	async def on_ip_geo_lookup_changed(self, event_name):
		L.info("Lookup loaded!")

	
	def process(self, context, event):
		if 'ip_address' not in event:
			return None

		event['L'] = self.Lookup.lookup_location_ipv4(event["ip_address"])
		return event


class MyProcessorIPV6(bspump.Processor):

	def __init__(self, app, pipeline, id=None, config=None):
		super().__init__(app, pipeline, id, config)
		svc = app.get_service("bspump.PumpService")
		self.Lookup = svc.locate_lookup("IPGeoLookup")
		self.Lookup.PubSub.subscribe("bspump.Lookup.changed!", self.on_ip_geo_lookup_changed)

	async def on_ip_geo_lookup_changed(self, event_name):
		L.warning("lookup loaded!")

	
	def process(self, context, event):
		if 'ip_address' not in event:
			return None

		event['L'] = self.Lookup.lookup_location_ipv6(event["ip_address"])
		return event


if __name__ == '__main__':
	app = MyApplication()
	app.run()
