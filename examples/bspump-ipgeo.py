from bspump.lookup import IPGeoLookup

from bspump.file import FileCSVSource
from bspump.trigger import OpportunisticTrigger
from bspump.common import PPrintSink
from bspump import BSPumpApplication, Pipeline, Processor
import logging


L = logging.getLogger(__name__)

class MyApplication(BSPumpApplication):
	def __init__(self):
		super().__init__()

		svc = self.get_service("bspump.PumpService")
		self.IPGeoLookup = IPGeoLookup(self, "IPGeoLookup")
		svc.add_lookup(self.IPGeoLookup)

		svc.add_pipeline(MyPipeline(self))
		

class MyPipeline(Pipeline):

	def __init__(self, app, pipeline_id=None):
		super().__init__(app, pipeline_id)
		self.build(
			FileCSVSource(app, self).on(OpportunisticTrigger(app)),
			# chose ipv4 or ipv6 processor
			#MyProcessorIPV4(app, self),
			MyProcessorIPV6(app, self), 
			PPrintSink(app, self)
		)

class MyProcessorIPV4(Processor):

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

class MyProcessorIPV6(Processor):

	def __init__(self, app, pipeline, id=None, config=None):
		super().__init__(app, pipeline, id, config)
		svc = app.get_service("bspump.PumpService")
		self.Lookup = svc.locate_lookup("IPGeoLookup")
		self.Lookup.PubSub.subscribe("bspump.Lookup.changed!", self.on_ip_geo_lookup_changed)

	async def on_ip_geo_lookup_changed(self, event_name):
		L.warn("lookup loaded!")

	
	def process(self, context, event):
		if 'ip_address' not in event:
			return None

		event['L'] = self.Lookup.lookup_location_ipv6(event["ip_address"])
		return event




if __name__ == '__main__':
	app = MyApplication()
	app.run()
