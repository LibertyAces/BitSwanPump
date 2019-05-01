from bspump import BSPumpApplication, Pipeline, Processor
from bspump.file import FileCSVSource
from bspump.trigger import OpportunisticTrigger
from bspump.common import PPrintSink, NullSink
from bspump.filter import ContentFilter

import logging
import string
import random


##
L = logging.getLogger(__name__)
##


class MyApplication(BSPumpApplication):
	def __init__(self):
		super().__init__()

		svc = self.get_service("bspump.PumpService")
		svc.add_pipeline(MyPipeline(self))
		

class MyPipeline(Pipeline):
	def __init__(self, app, pipeline_id=None):
		super().__init__(app, pipeline_id)
		query = {
			"$or":
				[
					{
						"user":
							{
								'$in':["user_0", "user_2", "user_10"]
							}
					}, 
					{
						"num":
							{
								"$gte": 500
							}
					},
					{
						"st":{
							"$regex":"/^L/i"
						}
					}
				]
		}
		self.build(
			FileCSVSource(app, self, 
				config={
					"post":"noop",
				 	"path":"test.csv"
				 }).on(OpportunisticTrigger(app)),
			RandomProcessor(app, self), 
			MyContentFilter(app, self, query),
			PPrintSink(app, self),
		)


class RandomProcessor(Processor):
	
	def process(self, context, event):
		st = ''.join(random.choice(string.ascii_uppercase) for _ in range(4))
		event["st"] = st
		
		num = random.randint(0, 1000)
		event["num"] = num
		return event


class MyContentFilter(ContentFilter):
	def do_on_hit(self, event):
		event["tag"] = ":)"
		return event


	def do_on_miss(self, event):
		event["tag"] = ":("
		return event



if __name__ == '__main__':
	app = MyApplication()
	app.run()
