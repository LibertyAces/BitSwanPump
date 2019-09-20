import asab.metrics
from .profiler import ProfilingCounter


class ProfilingService(asab.metrics.MetricsService):
	def create_profiling_counter(self, metric_name, tags):
		dimension = asab.metrics.service.metric_dimension(metric_name, tags)

		if dimension in self.Metrics:
			raise RuntimeError("Metric '{}' already present".format(dimension))

		if tags is not None:
			t = self.Tags.copy()
			t.update(tags)
		else:
			t = self.Tags

		m = ProfilingCounter(metric_name, tags=t)
		self._add_metric(dimension, m)
		return m
