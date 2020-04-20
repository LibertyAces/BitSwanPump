import numpy as np
import os


class WarmingUpCount(object):
	def __init__(self, size):
		self.DType = 'i8'
		self.WUC = np.zeros(size, dtype=self.DType)


	def decrease(self, indexes):
		self.WUC[indexes] -= 1
		self.WUC[self.WUC < 0] = 0


	def extend(self, size, value):
		start = self.WUC.shape[0]
		end = size
		self.WUC.resize(size, refcheck=False)
		self.WUC[start:end] = value


	def assign(self, index, value):
		self.WUC[index] = value


	def flush(self, indexes):
		self.WUC = self.WUC.take(indexes, axis=0)


	def create(self, size):
		pass


	def __len__(self):
		return self.WUC.shape[0]


class PersistentWarmingUpCount(WarmingUpCount):
	def __init__(self, path, size):
		super().__init__(size)
		self.Path = path
		if os.path.exists(self.Path):
			self.WUC = np.memmap(self.Path, dtype=self.DType, mode='readwrite')
		else:
			self.create(size)


	def extend(self, size, value):
		start = self.WUC.shape[0]
		end = size
		wuc = np.zeros(self.WUC.shape[0], dtype=self.DType)
		wuc[:] = self.WUC[:]
		wuc.resize(size, refcheck=False)
		self.WUC = np.memmap(self.Path, dtype=self.DType, mode='w+', shape=wuc.shape)
		self.WUC[:] = wuc[:]
		self.WUC[start:end] = value


	def flush(self, indexes):
		super().flush(indexes)
		self.create(self.WUC.shape[0])


	def create(self, size):
		wuc = np.memmap(self.Path, dtype=self.DType, mode='w+', shape=(size,))
		wuc[:] = self.WUC[:]
		self.WUC = wuc
