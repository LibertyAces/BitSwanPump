# BSPump tutorial

This tutorial shows how to create a simple pipeline that consumes data from TCP and print them on screen.

## Prerequisites

1. Python 3.7
2. pip for 3.7
3. `pip3 install -U asab`
4. `pip3 install -U aiohttp`
5. `pip3 install -U git+https://github.com/LibertyAces/BitSwanPump.git`


## Part 1 - BSPump micro-service app. skeleton

```
#!/usr/bin/env python3
import bspump

if __name__ == '__main__':
	app = bspump.BSPumpApplication()
	app.run()
```

## Part 2 - A first pipeline

```
#!/usr/bin/env python3
import bspump
import bspump.socket
import bspump.common

class MyPipeline(bspump.Pipeline):

	def __init__(self, app, pipeline_id):
		super().__init__(app, pipeline_id)
		self.build(
			bspump.socket.TCPSource(app, self, config={
				'host': '127.0.0.1',
				'port': 7777,
			}),
			bspump.common.PPrintSink(app, self)
		)	


if __name__ == '__main__':
	app = bspump.BSPumpApplication()

	svc = app.get_service("bspump.PumpService")
	svc.add_pipeline(MyPipeline(app, "MyPipeline"))
	
	app.run()
```

Test with:

```
nc -v 127.0.0.1 7777
```
