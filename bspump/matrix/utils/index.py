import numpy as np
import os
import collections


class Index(object):
	def __init__(self):
		self.N2IMap = collections.OrderedDict()
		self.I2NMap = collections.OrderedDict()


	def pop_index(self, index):
		if index in self.I2NMap:
			row_name = self.I2NMap.pop(index)
			del self.N2IMap[row_name]
			return True
		return False


	def get_row_index(self, row_name):
		return self.N2IMap.get(row_name)


	def get_row_name(self, row_index):
		return self.I2NMap.get(row_index)


	def add_row(self, name, index):
		self.N2IMap[name] = index
		self.I2NMap[index] = name


	def flush(self, indexes):
		n2imap = collections.OrderedDict()
		i2nmap = collections.OrderedDict()
		i = 0
		saved_indexes = []
		for row_name, row_index in self.N2IMap.items():
			if row_index not in indexes:
				n2imap[row_name] = i
				i2nmap[i] = row_name
				saved_indexes.append(row_index)
				i += 1

		self.N2IMap = n2imap
		self.I2NMap = i2nmap
		return saved_indexes


	def serialize(self):
		return {
			"N2IMap": self.N2IMap,
			"I2NMap": self.I2NMap,
		}


	def deserialize(self, data):
		self.N2IMap = data["N2IMap"]
		self.I2NMap = data["I2NMap"]


	def extend(self, size):
		pass


	def __contains__(self, row_name):
		if row_name in self.N2IMap:
			return True
		
		return False


	def __len__(self):
		return len(self.N2IMap)



class PersistentIndex(Index):
	def __init__(self, path, size):
		super().__init__()
		self.DType = 'U30'
		self.Path = path
		
		if os.path.exists(self.Path):
			self.Map = np.memmap(self.Path, dtype=self.DType, mode='readwrite')
			for i in range(len(self.Map)):
				value = self.Map[i]
				if value != '':
					self.I2NMap[i] = value
					self.N2IMap[value] = i
		else:
			if size is None:
				raise RuntimeError("The size should correspond to array size")
			
			self.Map = np.memmap(self.Path,  dtype=self.DType, mode='w+', shape=(size,))


	def pop_index(self, index):
		if super().pop_index(index):
			self.Map[index] = ''
			return True
		return False


	def add_row(self, name, index):
		super().add_row(name, index)
		self.Map[index] = name


	def extend(self, size): 
		map_ = np.zeros(self.Map.shape[0], dtype=self.DType)
		map_[:] = self.Map[:]
		map_.resize(size, refcheck=False)
		self.Map = np.memmap(self.Path,  dtype=self.DType, mode='w+', shape=map_.shape)
		self.Map[:] = map_[:]


	def flush(self, closed_indexes):
		saved_indexes = super().flush(closed_indexes)
		self.Map = self.Map.take(saved_indexes, axis=0)
		map_ = np.memmap(self.Path, dtype=self.DType, mode='w+', shape=self.Map.shape)
		map_[:] = self.Map[:]
		self.Map = map_
		return saved_indexes

