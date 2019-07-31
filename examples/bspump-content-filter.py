import logging
import random
import string

import bspump
import bspump.common
import bspump.file
import bspump.filter
import bspump.trigger

##

L = logging.getLogger(__name__)

##


class MyApplication(bspump.BSPumpApplication):
	def __init__(self):
		super().__init__()

		svc = self.get_service("bspump.PumpService")
		svc.add_pipeline(MyPipeline(self))
		

class MyPipeline(bspump.Pipeline):
	def __init__(self, app, pipeline_id=None):
		super().__init__(app, pipeline_id)

		query = {'$or': [
			{'user': {'$in': ['user_0', 'user_2', 'user_10']}},
			{'num': {'$gte': 500}},
			{'st': {'$regex': '/^L/i'}}
		]}
		self.build(
			bspump.file.FileCSVSource(app, self, config={
				"post": "noop",
				"path": "./data/users.csv"
			}).on(bspump.trigger.OpportunisticTrigger(app)),

			RandomProcessor(app, self),
			MyContentFilter(app, self, query),
			bspump.common.PPrintSink(app, self),
		)


class RandomProcessor(bspump.Processor):
	
	def process(self, context, event):
		st = ''.join(random.choice(string.ascii_uppercase) for _ in range(4))
		event["st"] = st
		
		num = random.randint(0, 1000)
		event["num"] = num
		return event


class MyContentFilter(bspump.filter.ContentFilter):
	def on_hit(self, context, event):
		event["tag"] = ":)"
		return event


	def on_miss(self, context, event):
		event["tag"] = ":("
		return event


if __name__ == '__main__':
	app = MyApplication()
	app.run()
