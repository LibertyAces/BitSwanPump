from collections import namedtuple

import asab.metrics.metrics


class ProfilerCounter(asab.metrics.metrics.Metric):
	"""
	Counter used for profiling application
	"""

	Measured = namedtuple('Measured', ['time_total', 'run_count'])

	def __init__(self, name, tags, reset: bool = False):
		super().__init__(name=name, tags=tags)
		self.Reset = reset
		self.Init = {}
		self.Values = {}

	def flush(self) -> dict:
		ret = self.Values
		if self.Reset:
			self.Values = self.Init.copy()
		return ret

	def add_measured_time(self, processor, value):
		"""
		Add custom measured time to processor.
		Initialize new metrics if processor haven't been measured yet
		"""
		try:
			measured, count = self.Values[processor.Id]
		except KeyError:
			self.Init[processor.Id] = self.Measured(0, 0)
			self.Values[processor.Id] = self.Measured(value,  1)
		else:
			measured += value
			count += 1

			self.Values[processor.Id] = self.Measured(measured, count)

	def rest_get(self):
		rest = super().rest_get()
		rest['Values'] = self.Values
		return rest

