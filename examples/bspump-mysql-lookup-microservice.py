import bspump
import bspump.web
import bspump.mysql
import aiohttp.web


class MyApplication(bspump.BSPumpApplication):
	def __init__(self):
		super().__init__()

		svc = self.get_service("bspump.PumpService")

		mysql_connection = bspump.mysql.MySQLConnection(self, "MySQLConnection", config={
			"user": "root",
			"password": "root_password",
			"db": "users",
		})

		svc.add_connection(mysql_connection)

		self.MySQLLookup = bspump.mysql.MySQLLookup(self, connection=mysql_connection, id="MySQLLookup", config={
			'from': 'user_loc',
			'key': 'user',
		})

		svc.add_lookup(self.MySQLLookup)


def webservice(request):
	svc = app.get_service("bspump.PumpService")
	Lookup = svc.locate_lookup("MySQLLookup")
	defined_keys = ['user_0', 'user_1']
	data = []
	for i in defined_keys:
		data.append(Lookup.get(i))
	return aiohttp.web.Response(text=str(data))


if __name__ == '__main__':
	app = MyApplication()

	app.add_module(bspump.web.Module)
	websvc = app.get_service("asab.WebService")

	websvc.WebApp.router.add_get('/querry_result', webservice)

	app.run()
