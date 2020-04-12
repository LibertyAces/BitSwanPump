import numpy as np
import os


class TimeConfig(object):
	def __init__(self, resolution, columns, start):
		self.DType = [
			('resolution', 'f8'),
			('columns', 'i8'),
			('start', 'i8'),
			('end', 'i8'),
		] 
		self.TC = np.zeros(1, dtype=self.DType)
		self.TC['resolution'] = resolution
		self.TC['columns'] = columns
		self.TC['start'] = start
		self.TC['end'] = start - (resolution * columns)


	def get_resolution(self):
		return self.TC['resolution']

	def get_columns(self):
		return self.TC['columns']

	def get_start(self):
		return self.TC['start']

	def get_end(self):
		return self.TC['end']

	def set_resolution(self, resolution):
		self.TC['resolution'] = resolution

	def set_start(self, start):
		self.TC['start'] = start

	def set_end(self, end):
		self.TC['end'] = end

	def add_start(self, time):
		self.TC['start'] += time

	def add_end(self, time):
		self.TC['end'] += time


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

