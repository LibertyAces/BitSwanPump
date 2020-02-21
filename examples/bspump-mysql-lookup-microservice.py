import bspump
import bspump.mysql
import bspump.web
import aiohttp.web


class MyApplication(bspump.BSPumpApplication):
	"""
	Example microservice serving preconfigured MySQL querry.
	Example setup:
		- run MySQL in docker: $ docker run --rm -p 3306:3306 -e MYSQL_ROOT_PASSWORD=root_password mysql
		- connect using: $  mysql -h 127.0.0.1 -P 3306 -u root -p
		- type password
		- create database and switch into it:
			- mysql> create database users;
			- mysql> use users
		- create table:
			- mysql> CREATE TABLE user_loc (id INT NOT NULL AUTO_INCREMENT, user CHAR(30), lat FLOAT(9,6), lon FLOAT(9,6), PRIMARY KEY (id));
		- create some records:
			- mysql> INSERT INTO user_loc (user, lat, lon) VALUES ("user_0", 37.405992,-122.078515),("user_1", 50.08804, 14.42076);
		- run the example
		- You can now fire a GET request to localhost:8080/query_result
	"""
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
	"""
	Here, we get the bspump service, and from it, we localize the MySQLLookup using their respective id strings.
	That gives us access to the Lookup, and we are able to serve its contents, using the keys we define, in the
	response.
	"""
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

	websvc.WebApp.router.add_get('/query_result', webservice)

	app.run()
