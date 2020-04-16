import numpy as np
import os


class TimeConfig(object):
	def __init__(self, resolution, columns, start):
		self.DType = [
			('resolution', 'f8'),
			('columns', 'i8'),
			('start', 'f8'),
			('end', 'f8'),
		] 
		self.TC = np.zeros(1, dtype=self.DType)
		self.TC['resolution'][0] = resolution
		self.TC['columns'][0] = columns
		self.TC['start'][0] = start
		self.TC['end'][0] = start - (resolution * columns)


	def get_resolution(self):
		return self.TC['resolution'][0]

	def get_columns(self):
		return self.TC['columns'][0]

	def get_start(self):
		return self.TC['start'][0]

	def get_end(self):
		return self.TC['end'][0]

	def set_resolution(self, resolution):
		self.TC['resolution'][0] = resolution

	def set_start(self, start):
		self.TC['start'][0] = start

	def set_end(self, end):
		self.TC['end'][0] = end

	def add_start(self, time):
		self.TC['start'][0] += time

	def add_end(self, time):
		self.TC['end'][0] += time


class PersistentTimeConfig(TimeConfig):
	def __init__(self, path, resolution, columns, start):
		super().__init__(resolution, columns, start)
		self.Path = path
		if os.path.exists(self.Path):
			self.TC = np.memmap(self.Path, dtype=self.DType, mode='readwrite')
		else:
			tc = np.memmap(self.Path, dtype=self.DType, mode='w+', shape=(1,))
			tc[:] = self.TC[:]
			self.TC = tc

