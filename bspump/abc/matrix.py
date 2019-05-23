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
		Each column has name and type. Types can be identified from table:

		'b'	Byte	np.dtype('b')
		'i'	Signed integer	np.dtype('i4') == np.int32
		'u'	Unsigned integer	np.dtype('u1') == np.uint8
		'f'	Floating point	np.dtype('f8') == np.int64
		'c'	Complex floating point	np.dtype('c16') == np.complex128
		'S', 'a'	String	np.dtype('S5')
		'U'	Unicode string	np.dtype('U') == np.str_
		'V'	Raw data (void)	np.dtype('V') == np.void

		storage has structure:
		{
			"row_id0":{
				"storage_id0": object,
				...
			},
			...
		}

		It is possible to specify the column as a matrix with different dimension, the tuple (second_dim, third_dim, ...). 
		E.g: '(4, 3)i8' will create for each row the matrix 
		[0 0 0
		 0 0 0
		 0 0 0
		 0 0 0]

	'''

	def __init__(self, app, column_names, column_formats, id=None, config=None):
		self.Id = id if id is not None else self.__class__.__name__
		super().__init__("matrix:{}".format(self.Id), config=config)
		self.ColumnNames = column_names
		self.ColumnFormats = column_formats
		
		self.RowMap = collections.OrderedDict()
		self.RevRowMap = collections.OrderedDict()
		self.Storage = {}
		self.ClosedRows = set()
		self.Matrix = np.zeros(0, dtype={'names':self.ColumnNames, 'formats':self.ColumnFormats})


	def rebuild_rows(self, mode):	
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


	#@abc.abstractmethod
	async def analyze(self):
		pass

