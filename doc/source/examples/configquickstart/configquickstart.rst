.. _config:

Configuration Quickstart
========================

In this tutorial you will learn about configuration in BSPump and how to use it.

What is configuration?
----------------------
Every BitSwan object inside BSPump application can be configured using user-defined configuration options.
It's good practice to write configuration in ``.conf`` files, because when you will need to change something
in your code you basically change it just in ``.conf`` file.

Every object has default configuration values set in ``ConfigDefaults``, if you set ``ConfigDefaults`` in your specific
class you override ``ConfigDefaults`` which are inherited from parent class.

Configuration ``.conf`` files in are built-in in ASAB, the platform on which BSPump is build on. You can find more
about it in `ASAB documentation <https://asab.readthedocs.io/en/latest/asab/config.html>`_

**There are 3 types how you can configure object**

1. By defining ``ConfigDefaults`` dictionary inside specific class
::
   class MySQLSource(TriggerSource):

   	ConfigDefaults = {
   		'query': 'SELECT id, name, surname FROM people;'
        }

2.Using ``config`` parameter in the object's constructor
::
    bspump.mysql.MySQLSource(app, self, "MySQLConnection1", config={'query': 'SELECT id, name, surname FROM people;'})

3. By creating ``.conf`` file
::
    [pipeline:PipelineID:MySQLSource]
     'query': 'SELECT id, name, surname FROM people;'

Example
-------
This example shows how to create configuration file for get data from API via basic HTTPClientSource.

In first step we create .conf file where we store API key
::
    [pipeline:SamplePipeline:HTTPClientSource]
    api_key = <YOUR PRIVATE API KEY>

``[pipeline:SamplePipeline:HTTPClientSource]`` in this line we specified which class the configuration applies to.
Values below this line override the same values in ``ConfigDefaults`` of specified classes.

In next step we have a sample pipeline which gets data through https://openweathermap.org/ API using API key from .conf
file. See more in :ref:`coindesk`.
::
    class SamplePipeline(bspump.Pipeline):

	def __init__(self, app, pipeline_id):
		super().__init__(app, pipeline_id)

		self.build(
			bspump.http.HTTPClientSource(app, self, config={
				'url': f"https://api.openweathermap.org/data/2.5/weather?q=London&units=metric&appid={self.Config['api_key']}"
			}).on(bspump.trigger.PeriodicTrigger(app, 1)),
			bspump.common.StdJsonToDictParser(app, self),
			bspump.common.PPrintSink(app, self),
		)

Configuration in .conf file is accessible via self.Config method (in this case we use ``self.Config['api_key']`` to get
API key from our ``.conf`` file)
