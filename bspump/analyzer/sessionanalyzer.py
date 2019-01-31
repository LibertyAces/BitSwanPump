import time
import logging
import numpy as np

import asab

from .analyzer import Analyzer

###

L = logging.getLogger(__name__)

###


class SessionAnalyzer(Analyzer):
	
	'''
	Sessions are table with rows linked to session_id and columns
	with specified column name, which has specfied column format. Example of usage:
	a) self.Sessions[integer_session_index] returns whole session row with all fields;
	b) self.Sessions[column_name] returns matrix with columns for all indexes
	c) self.Sessions[integer_session_index][column_name] returns specific element row-column
	
	Each column has name and type. Types can be identified from table:
	
	'b'	Byte	np.dtype('b')
	'i'	Signed integer	np.dtype('i4') == np.int32
	'u'	Unsigned integer	np.dtype('u1') == np.uint8
	'f'	Floating point	np.dtype('f8') == np.int64
	'c'	Complex floating point	np.dtype('c16') == np.complex128
	'S', 'a'	String	np.dtype('S5')
	'U'	Unicode string	np.dtype('U') == np.str_
	'V'	Raw data (void)	np.dtype('V') == np.void
	'''


	def __init__(self, app, pipeline, column_formats, column_names, id=None, config=None):
		
		super().__init__(app, pipeline, id, config)
		self.ColumnNames = column_names
		self.ColumnFormats = column_formats
		if len(self.ColumnNames) != len(self.ColumnFormats):
			raise RuntimeError("Column names and column formats should be the same length!")

		self.ColumnNames.append("@timestamp_start")
		self.ColumnFormats.append('i4')

		self.ColumnNames.append("@timestamp_end")
		self.ColumnFormats.append('i4')
		self._initialize_sessions()
		

	def _initialize_sessions(self):
		self.Sessions = np.zeros(0, dtype={'names': self.ColumnNames, 'formats': self.ColumnFormats})
		self.RowMap = {}
		self.RevRowMap = {}
		self.ClosedRows = set()


	def add_session(self, session_id, start_time):
		row = np.zeros(1, dtype={'names': self.ColumnNames, 'formats': self.ColumnFormats})
		row["@timestamp_start"] = start_time
		self.Sessions = np.append(self.Sessions, row) #discussable, we can preassign big matrix and then fill it untill end and then restructure
		row_counter = len(self.RowMap)
		self.RowMap[session_id] = row_counter
		self.RevRowMap[row_counter] = session_id


	def close_session(self, session_id, end_time):
		row_counter = self.RowMap.get(session_id)
		
		if row_counter is None:
			return
		else:
			idx = self.RowMap[session_id]
			self.Sessions[idx]['@timestamp_end'] = end_time
			self.ClosedRows.add(row_counter)


	def rebuild_sessions(self, mode):
		
		if mode == "full":
			self._initialize_sessions()
		elif mode == "partial":
			new_row_map = {}
			new_rev_row_map = {}
			saved_indexes = []
			for key in self.RowMap.keys():
				value = self.RowMap[key]
				if value not in self.ClosedRows:
					new_row_map[key] = value
					new_rev_row_map[value] = key
					saved_indexes.append(value)

			new_sessions = self.Sessions[saved_indexes]
			self.Sessions = new_sessions
			self.RowMap = new_row_map
			self.RevRowMap = new_rev_row_map
			self.ClosedRows = set()

		else:
			L.warn("Unknown mode")

	
	
	





	

