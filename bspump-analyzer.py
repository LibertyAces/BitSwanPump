from bspump.analyzer import Analyzer

class MyAnalyzer(Analyzer):
	def __init__(self, app, pipeline, id=None, config=None):
		super().__init__(app, pipeline, id=id, config=config)

		#introducing entity to analyze
		self.SumOfEventFields = 0

	# simple check if the event contains necessary fields
	def predicate(self, event):
		if "some_field" not in event:
			return False

		return True

	# record something from event to analyzer's internal structure
	def evaluate(self, event):
		self.SumOfEventFields += event["some_field"]

	# analyze the structure
	async def analyze(self):
		if self.SumOfEventFields == 0:
			print("Something went wrong")
			
