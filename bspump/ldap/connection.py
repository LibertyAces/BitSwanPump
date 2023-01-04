import contextlib
import logging
import ldap
import ldap.resiter

from ..abc.connection import Connection

#

L = logging.getLogger(__name__)

#


class LDAPObject(ldap.ldapobject.LDAPObject, ldap.resiter.ResultProcessor):
	pass


class LDAPConnection(Connection):
	"""
	Examples of configurations:

	[connection:ldap]
	host=12.34.56.78
	port=27017
	username=cn=admin,dc=example,dc=org
	password=abc123def456

	[connection:ldap]
	uri=ldaps://localhost:636
	username=cn=admin,dc=example,dc=org
	password=abc123def456
	"""

	ConfigDefaults = {
		"host": "localhost",
		"port": 0,  # = use the default 389 for non-secure and 636 for secure connection
		"uri": "",
		"username": "cn=admin,dc=example,dc=org",
		"password": "admin",

		# Path to CA file in PEM format
		"tls_cafile": "",

		# Certificate policy.
		# Possible options (from python-ldap docs):
		# "never"  - Don’t check server cert and host name
		# "allow"  - Used internally by slapd server.
		# "demand" - Validate peer cert chain and host name
		# "hard"   - Same as "demand"
		"tls_require_cert": "never",

		"network_timeout": "10",  # set network_timeout to -1 for no timeout
	}

	def __init__(self, app, id=None, config=None):
		super().__init__(app, id=id, config=config)
		self.TLSEnabled = len(self.Config.get("tls_cafile")) > 0
		self.URI = self.Config.get("uri")
		self.Host = self.Config.get("host")
		self.Port = self.Config.getint("port")
		if self.Port == 0:
			self.Port = 636 if self.TLSEnabled else 389
		if len(self.URI) == 0:
			self.URI = "{scheme}://{host}:{port}".format(
				scheme="ldaps" if self.TLSEnabled else "ldap",
				host=self.Host,
				port=self.Port
			)

	@contextlib.contextmanager
	def ldap_client(self):
		client = LDAPObject(self.URI)
		client.protocol_version = ldap.VERSION3
		client.set_option(ldap.OPT_REFERRALS, 0)
		client.set_option(ldap.OPT_NETWORK_TIMEOUT, int(self.Config.get("network_timeout")))
		if self.TLSEnabled:
			self._enable_tls(client)

		try:
			client.simple_bind_s(self.Config.get("username"), self.Config.get("password"))
			yield client
		except Exception as e:
			L.error("Cannot connect to LDAP server: {}".format(e), exc_info=True, struct_data={"ldap_uri": self.URI})
		finally:
			client.unbind_s()

	def _enable_tls(self, client):
		tls_cafile = self.Config.get("tls_cafile")
		tls_require_cert = self.Config.get("tls_require_cert")
		if len(tls_cafile) > 0:
			client.set_option(ldap.OPT_X_TLS_CACERTFILE, tls_cafile)
		if tls_require_cert == "never":
			client.set_option(ldap.OPT_X_TLS_REQUIRE_CERT, ldap.OPT_X_TLS_NEVER)
		elif tls_require_cert == "demand":
			client.set_option(ldap.OPT_X_TLS_REQUIRE_CERT, ldap.OPT_X_TLS_DEMAND)
		elif tls_require_cert == "allow":
			client.set_option(ldap.OPT_X_TLS_REQUIRE_CERT, ldap.OPT_X_TLS_ALLOW)
		elif tls_require_cert == "hard":
			client.set_option(ldap.OPT_X_TLS_REQUIRE_CERT, ldap.OPT_X_TLS_HARD)
		else:
			raise ValueError("Invalid 'tls_require_cert' value: {}.")
		client.set_option(ldap.OPT_X_TLS_NEWCTX, 0)
