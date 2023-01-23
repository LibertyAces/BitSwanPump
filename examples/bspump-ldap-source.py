#!/usr/bin/env python3
import logging
import bspump
import bspump.common
import bspump.trigger
import bspump.ldap

###

L = logging.getLogger(__name__)

###


class NormalizeProcessor(bspump.Processor):
	def process(self, context, event):
		event_out = {}
		for k, v in event.items():
			if k in ("dn", "sAMAccountName", "email", "givenName", "sn"):
				event_out[k] = k.decode("ascii")
			elif k in ("createTimestamp", "modifyTimestamp"):
				event_out[k] = int(k)
			elif k == "objectGUID":
				event_out["id"] = k.hex()
			elif k == "UserAccountControl":
				event_out["suspended"] = int(event["userAccountControl"]) & 2 == 2
		return event


class LDAPPipeline(bspump.Pipeline):
	def __init__(self, app, pipeline_id):
		super().__init__(app, pipeline_id)
		self.build(
			bspump.ldap.LDAPSource(app, self, "LDAPConnection").on(bspump.trigger.PubSubTrigger(app, "RunLDAPPipeline!")),
			NormalizeProcessor(app, self),
			bspump.common.PPrintSink(app, self)
		)


if __name__ == "__main__":
	"""
	This simple pipeline connects to LDAP, retrieves user data and prints them to stdout.

	Make sure to update the connection and source config with the credentials for your LDAP server.
	"""
	app = bspump.BSPumpApplication()
	svc = app.get_service("bspump.PumpService")

	# Create LDAP connection
	svc.add_connection(
		bspump.ldap.LDAPConnection(app, "LDAPConnection")
	)

	# Construct and register the pipeline
	pl = LDAPPipeline(app, "LDAPPipeline")
	svc.add_pipeline(pl)

	# Trigger the pipeline
	app.PubSub.publish("RunLDAPPipeline!", asynchronously=True)

	app.run()
