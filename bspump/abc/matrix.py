import time
import logging

import numpy as np

import asab
import collections
import abc


###

L = logging.getLogger(__name__)

###


class MatrixABC(abc.ABC, asab.ConfigObject):
	'''
		General `Matrix` object.
		`column_formats` is an array, each element contains the letter from the table + number:

			+------------+------------------+
			| Name       | Definition       |
			+============+==================+
			| 'b'        | Byte             |
			+------------+------------------+
			| 'i'        | Signed integer   |
			+------------+------------------+
			| 'u'        | Unsigned integer |
			+------------+------------------+
			| 'f'        | Floating point   |
			+------------+------------------+
			| 'c'        | Complex floating |
			|            | point            |
			+------------+------------------+
			| 'S'        | String           |
			+------------+------------------+
			| 'U'        | Unicode string   |
			+------------+------------------+
			| 'V'        | Raw data         |
			+------------+------------------+

		Example: 'i8' stands for int64.
		It is possible to create a matrix with elements of specified format. The tuple with number of dimensions should 
		stand before the letter.
		Example: '(6, 3)i8' will create the matrix with n rows, 6 columns and 3 third dimensions with integer elements.
		`column_names` is an array with names of each column, with the same length as `column_formats`.
		
		Object main attributes:
		`Matrix` is numpy matrix, where number of rows is a number of unique ids and
		specified columns.
		`RowMap` is a mapping from a event unique id to the matrix row index.
		`RevRowMap` is a mapping from matrix row index to unique id.
		`Storage` is a dictionary without specific structure, where additional 
		information can be kept.
		`ClosedRows` is a set, where some row ids can be stored before deletion during the matrix rebuild.

	'''


	def __init__(self, app, column_names, column_formats, id=None, config=None):
		self.Id = id if id is not None else self.__class__.__name__
		super().__init__("matrix:{}".format(self.Id), config=config)

		self.App = app
		self.Loop = app.Loop

		self.ColumnNames = column_names
		self.ColumnFormats = column_formats

		self.RowMap = collections.OrderedDict()
		self.RevRowMap = collections.OrderedDict()
		self.Storage = {}
		self.ClosedRows = set()
		self.Matrix = np.zeros(0, dtype={'names':self.ColumnNames, 'formats':self.ColumnFormats})


	def time(self):
		return self.App.time()


	def rebuild_rows(self, mode):
		'''
			Function meant to rebuild the matrix.
			`mode` can be `full`, which means the matrix will be recreated, 
			or `partial`, which means the matrix will be recreated without rows
			from `ClosedRows`.
		'''
	
		if mode == "full":
			self.RowMap = collections.OrderedDict()
			self.RevRowMap = collections.OrderedDict()
			self.Storage = {}
			self.ClosedRows = set()
			self.Matrix = np.zeros(0, dtype={'names':self.ColumnNames, 'formats':self.ColumnFormats})
			
		elif mode == "partial":
			new_row_map = collections.OrderedDict()
			new_rev_row_map = collections.OrderedDict()
			saved_indexes = []
			i = 0
			for key in self.RowMap.keys():
				value = self.RowMap[key]
				if value not in self.ClosedRows:
					new_row_map[key] = i
					new_rev_row_map[i] = key
					saved_indexes.append(value)
					i += 1
				else:
					if value in self.Storage:
						self.Storage.pop(value)
			new_matrix = self.Matrix[saved_indexes]
			self.Matrix = new_matrix
			self.RowMap = new_row_map
			self.RevRowMap = new_rev_row_map
			self.ClosedRows = set()
		else:
			L.warn("Unknown mode '{}'".format(mode))

	
	def get_row(self, row_name):
		return self.RowMap.get(row_name)


	def get_row_id(self, row_idx):
		return self.RevRowMap.get(row_idx)


	#@abc.abstractmethod
	async def analyze(self):
		pass

