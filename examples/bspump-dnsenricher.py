import logging

import async_dns.resolver

import bspump
import bspump.common
import bspump.random
import bspump.trigger

##

L = logging.getLogger(__name__)

##


class DNSEnricher(bspump.Generator):
	"""
	Uses async_dns' resolver to get information about the hostname from IP address.
	"""

	def __init__(self, app, pipeline, id=None, config=None):
		super().__init__(app, pipeline, id, config)

		self.Resolver = async_dns.resolver.ProxyResolver()
		self.Resolver.set_proxies([
			"8.8.8.8"
		])


	async def generate(self, context, event, depth):

		if "ip" not in event:
			self.Pipeline.inject(context, event, depth)
			return

		res, cached = await self.Resolver.query(event["ip"])
		hostname = res.an[0].data.data

		event["dns_hostname"] = hostname
		event["dns_hostname_read_from_cache"] = cached
		self.Pipeline.inject(context, event, depth)


class DNSPipeline(bspump.Pipeline):
	"""
	Enrichers events with IP addresses with DNS records.

	Sample output:

	{
		'dns_hostname': 'prg03s12-in-f14.1e100.net',
		'dns_hostname_read_from_cache': True,
		'ip': '142.251.36.142'
	}
	{
		'dns_hostname': 'prg03s12-in-f14.1e100.net',
		'dns_hostname_read_from_cache': True,
		'ip': '142.251.36.142'
	}
	{
		'dns_hostname': 'prg03s10-in-f14.1e100.net',
		'dns_hostname_read_from_cache': True,
		'ip': '142.251.36.78'
	}
	"""

	def __init__(self, app, pipeline_id=None):
		super().__init__(app, pipeline_id)

		self.build(

			bspump.random.RandomSource(app, self, choice=[
				{"ip": "142.251.36.78"},
				{"ip": "142.251.36.142"},
				{"ip": "77.75.79.222"},
			], config={"number": 3}).on(bspump.trigger.OpportunisticTrigger(app, chilldown_period=10)),

			DNSEnricher(app, self),

			bspump.common.PPrintSink(app, self)
		)


class DNSApplication(bspump.BSPumpApplication):

	def __init__(self):
		super().__init__()
		svc = self.get_service("bspump.PumpService")
		svc.add_pipeline(DNSPipeline(self))


if __name__ == '__main__':
	app = DNSApplication()
	app.run()
