import collections

class LRUCacheDict(collections.OrderedDict):

	def __init__(self, app, max_size=1000, max_duration=None, *args, **kwargs):
		super().__init__(*args, **kwargs)

		self.App = app

		self.MaxSize = max_size
		self.MaxDuration = max_duration
		self.refresh()

	def refresh(self):
		# Remove items that overflow the dictionary
		if self.MaxSize:
			for i in range(max(0, len(self) - self.MaxSize)):
				self.popitem(last=False)

		# Remove items by max time
		if self.MaxDuration:
			limit = self.App.time() - self.MaxDuration
			while self:
				value, lru = next(iter(super().values()))
				if lru > limit:
					break
				self.popitem(last=False)

	def __getitem__(self, key):
		value = super().__getitem__(key)[0]
		super().__setitem__(key, (value, self.App.time()))
		self.move_to_end(key)
		return value

	def __setitem__(self, key, value):
		super().__setitem__(key, (value, self.App.time()))
		self.refresh()

	def items(self):
		return ((key, value) for key, (value, _) in super().items())

	def values(self):
		return (value for value, _ in super().values())
