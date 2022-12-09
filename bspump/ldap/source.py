import asyncio
import logging
from bspump.abc.source import TriggerSource

#

L = logging.getLogger(__name__)

#

class LDAPSource(TriggerSource):

	ConfigDefaults = {
		"filter": "(&(objectClass=inetOrgPerson)(cn=*))",
		"attributes": "sAMAccountName cn createTimestamp modifyTimestamp UserAccountControl email",
		"_results_per_page": 1000,
	}

	def __init__(self, app, pipeline, connection, query_parms=None, id=None, config=None):
		super().__init__(app, pipeline, id=id, config=config)
		self.Scope = ldap.SCOPE_SUBTREE
		self.Connection = pipeline.locate_connection(app, connection)
		self.Base = self.Config.get("base")
		self.Filter = self.Config.get("filter")
		self.Attributes = self.Config.get("attributes").split(" ")
		self.ResultsPerPage = self.Config.getint("_results_per_page")

	async def cycle(self):
		# TODO: Throttling
		await self.Pipeline.ready()
		while True:
			page, cookie = await self.ProactorService.execute(
				self._search_worker, cookie)
			async for entry in page:
				await self.process(entry, context={})
			if cookie is None or len(cookie) == 0:
				break

	def _search_worker(self, cookie=b""):
		page = []
		with self.Connection.ldap_client() as client:
			paged_results_control = ldap.controls.SimplePagedResultsControl(
				True,
				size=self.ResultsPerPage,
				cookie=cookie
			)
			msgid = client.search_ext(
				base=self.Base,
				scope=self.Scope,
				filterstr=self.Filter,
				attrlist=self.Attributes,
				serverctrls=[paged_results_control],
			)
			res_type, res_data, res_msgid, serverctrls = client.result3(msgid)
			for dn, attrs in res_data:
				page.append({"dn": dn, **attrs})

			for sc in serverctrls:
				if sc.controlType == ldap.controls.SimplePagedResultsControl.controlType:
					cookie = sc.cookie
			else:
				L.error("Server ignores RFC 2696 control: No serverctrls in result")

			return page, cookie
