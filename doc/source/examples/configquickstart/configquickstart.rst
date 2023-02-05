.. _config:

Configuration Quickstart
========================

In this tutorial you will learn about configuration in BSPump and how to use it.

What is configuration?
----------------------
Every BitSwan object inside BSPump application can be configured using user-defined configuration options.
It's good practice to write configuration in ``.conf`` files, because making changes will be much easier.

Every object has default configuration values set in ``ConfigDefaults``. If you set ``ConfigDefaults`` in your specific
class you override same values in ``ConfigDefaults``, which are inherited from the parent class.

Configuration ``.conf`` files in are built-in in ASAB, the platform on which BSPump is built. You can find more
about it in `ASAB documentation <https://asab.readthedocs.io/en/latest/asab/config.html>`_

**There are 3 methods to configure object**

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
    [pipeline:PipelineID]
    query = SELECT id, name, surname FROM people;

Example
-------
This example shows how to create a configuration file to get data from API via basic HTTPClientSource.

In first step we create .conf file where we store API key
::
    [pipeline:SamplePipeline]
    url = https://api.openweathermap.org/data/2.5/weather?q=London&units=metric&appid={api_key}
    api_key = <YOUR PRIVATE API KEY>

``[pipeline:SamplePipeline]`` in this line we specify which class the configuration applies to.
Values below this line override the same values in ``ConfigDefaults`` of specified classes.


Configuration in .conf file is accessible via self.Config method (in this case we use ``self.Config['api_key']`` to get
API key from our ``.conf`` file)

In next step we have a sample pipeline that gets data through https://openweathermap.org/ API using API's URL and API key from .conf
file. See more in :ref:`coindesk`.
::
    #!/usr/bin/env python3

    import bspump
    import bspump.common
    import bspump.http
    import bspump.trigger


    class SamplePipeline(bspump.Pipeline):

        def __init__(self, app, pipeline_id):
            super().__init__(app, pipeline_id)

            self.build(
                bspump.http.HTTPClientSource(app, self,
                config={'url': self.Config['url'].format(api_key = self.Config['api_key'])}).on(bspump.trigger.PeriodicTrigger(app, 2)),
                bspump.common.StdJsonToDictParser(app, self),
                bspump.common.PPrintSink(app, self)
            )


    if __name__ == '__main__':
        app = bspump.BSPumpApplication()

        svc = app.get_service("bspump.PumpService")
        # Construct and register Pipeline
        pl = SamplePipeline(app, 'SamplePipeline')
        svc.add_pipeline(pl)

        app.run()


Running your pump with configuration files
------------------------------------------
When you want to run your pump with configuration file there are two ways to do that.

In terminal
^^^^^^^^^^^
To run your pump with a configuration file, use ``-c`` switch in the terminal, after that switch there has to be ``file_path/file_name.conf``.

For example when you have configuration file in same folder
::
    ~python3 mypumptest.py -c mypumpconfiguration.conf

In your IDE
^^^^^^^^^^^
To run your pump in IDE you have to set the run parameters. For example in PyCharm you have to go to Run -> Edit Configurations...
and then change the run parameters to ``-c file_path/nameOfYourConfig.conf``

.. image:: ../testdoc/config1.png
    :width: 800
    :align: center
    :alt: IDE Configuration
