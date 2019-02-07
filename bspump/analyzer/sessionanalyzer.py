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



	sws_configuration = {'label0':{'column_formats':['c1', 'c2'], 'column_names':['col1', 'col12']}}
	if you need to create just one session matrix, name the label somehow and specify column_fomats/names. 
	you can access it by self.SessionMatrix without the label 
	'''


	def __init__(self, app, pipeline, sws_configuration, id=None, config=None):
		super().__init__(app, pipeline, id, config)
		self.ColumnNames = column_names
		self.ColumnFormats = column_formats
		

		self.ColumnNames.append("@timestamp_start")
		self.ColumnFormats.append('i4')

		self.ColumnNames.append("@timestamp_end")
		self.ColumnFormats.append('i4')
		self._create_sessions(app, pipeline, sws_configuration)
		

	def _create_sessions(self, app, pipeline, sws_configuration):
		self.SessionMatrixes = {}
		for label in sws_configuration.keys():
			self.SessionMatrixes[label] = SessionWindow(
				app,
				pipeline,
				column_formats=sws_configuration[label]['column_formats'],
				column_names=sws_configuration[label]['column_names'],
			)
		
		self.SessionMatrix = self.SessionMatrixes[list(sws_configuration.keys())[0]]



	def add_session(self, session_id, start_time, label=None):
		if label is None:
			self.SessionMatrix.add_row(session_id,start_time)		
		else:
			self.SessionMatrixes[label].add_row(session_id,start_time)



	def close_session(self, session_id, end_time, label=None):
		if label is None:
			s = self.SessionMatrix
		else:
			s = self.SessionMatrixes[label]
		
		s.close_row(session_id, end_time)


	def rebuild_sessions(self, mode, label=None):
		if label is None:
			s = self.SessionMatrix
		else:
			s = self.SessionMatrixes[label]

		s.rebuild_rows(mode)
		

	
	
	





	

