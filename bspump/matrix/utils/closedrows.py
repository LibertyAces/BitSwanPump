import numpy as np
import os


class ClosedRows(object):
	def __init__(self, max_len=None):
		self.CR = set()
		if max_len is None:
			max_len = float('inf')

		self.MaxLen = max_len


	def pop(self):
		return self.CR.pop()


	def get_rows(self):
		return self.CR


	def add(self, element):
		if len(self.CR) == self.MaxLen:
			raise RuntimeError("Maximum size exceeded")

		self.CR.add(element)


	def __contains__(self, element):
		if element in self.CR:
			return True
		return False


	def serialize(self):
		return list(self.get_rows())


	def deserialize(self, data):
		self.CR = set(data)


	def __len__(self):
		return len(self.CR)


	def extend(self, start, stop): 
		self.CR |= frozenset(range(start, stop)) #NO!
		if len(self.CR) >= self.MaxLen:
			raise RuntimeError("Maximum size exceeded")


	def flush(self, size=None):
		self.CR = set()




class PersistentClosedRows(ClosedRows):
	def __init__(self, path, size=None, max_len=None):
		super().__init__(max_len=max_len)
		self.DType = 'i1'
		self.Path = path
		if os.path.exists(self.Path):
			self.CRBit = np.memmap(self.Path, dtype=self.DType, mode='readwrite')
			for i in range(len(self.CRBit)):
				if self.CRBit[i] == 0:
					self.CR.add(i)
		else:
			if size is None:
				raise RuntimeError("The size should correspond to array size")
			self.CR.add(0)
			self.ones(size)


	def pop(self):
		element = super().pop()
		self.CRBit[element] = 1
		return element


	def add(self, element):
		super().add(element)
		self.CRBit[element] = 0


	def extend(self, start, stop):
		cr_ = np.zeros(self.CRBit.shape[0], dtype=self.DType)
		cr_[:] = self.CRBit[:]
		cr_.resize(stop, refcheck=False)
		self.CRBit = np.memmap(self.Path, dtype=self.DType, mode='w+', shape=cr_.shape)
		self.CRBit[:] = cr_[:]
		super().extend(start, stop)


	def flush(self, size):
		super().flush(size)
		self.ones(size)


	def ones(self, size):
		self.CRBit = np.memmap(self.Path, dtype=self.DType, mode='w+', shape=(size,))
		self.CRBit[:] = 1
