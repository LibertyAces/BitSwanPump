import logging

import bspump
import bspump.common
import bspump.mysql
import bspump.mysql.binlogsource

##

L = logging.getLogger(__name__)


##


class MyApplication(bspump.BSPumpApplication):
	"""

	## Try it out

	# Create and chown mysql lock

	$ sudo mkdir /var/run/mysqld
	$ sudo chown 999:999 /var/run/mysqld

	$ docker run --rm \
		-v /tmp/mysql_datadir:/var/lib/mysql \
		-v /var/run/mysqld/:/var/run/mysqld/ \
		-p 3306:3306 \
		-e MYSQL_ROOT_PASSWORD=root_password \
		mysql \
		mysqld \
		--datadir=/var/lib/mysql \
		--server-id=1 \
		--log-bin=/var/lib/mysql/mysql-bin.log \
		--binlog_do_db=sample_db

	# Insert some sample data in your database
	```
		mysql> create database sample_db;
		mysql> use sample_db;
		mysql> CREATE TABLE people (id INT NOT NULL AUTO_INCREMENT, name CHAR(30), surname CHAR(30), PRIMARY KEY (id));
		mysql> INSERT INTO people (name, surname) VALUES ("john", "doe"),("juan", "perez"),("wop", "wops");
	```
	# Chown binlog

	$ sudo chmod a+r /tmp/mysql_datadir/mysql-bin.000001

	"""
	def __init__(self):
		super().__init__()

		svc = self.get_service("bspump.PumpService")

		mysql_connection = bspump.mysql.MySQLConnection(self, "MySQLConnection", config={
			"user": "root",
			"password": "root_password",
			"db": "sample_db"
		})

		svc.add_connection(mysql_connection)
		svc.add_pipeline(MyPipeline(self))


class MyPipeline(bspump.Pipeline):
	def __init__(self, app, pipeline_id=None):
		super().__init__(app, pipeline_id)
		self.build(
			bspump.mysql.binlogsource.MySQLBinaryLogSource(app, self, "MySQLConnection", config={
				'server_id': 1,
				'log_file': '/tmp/mysql_datadir/mysql-bin.000001'
			}),
			bspump.common.PPrintSink(app, self)
		)


if __name__ == '__main__':
	app = MyApplication()
	app.run()
