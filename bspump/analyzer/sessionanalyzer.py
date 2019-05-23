import time
import logging
import numpy as np

import asab

from .analyzer import Analyzer
from .matrix import SessionMatrix

###

L = logging.getLogger(__name__)

###


class SessionAnalyzer(Analyzer):
	
	'''
	SessionAnalyzer operates over the SessionMatrixContainer object. It provides analyzis over the 
	specified MatrixContainers/ other informations about the sessions, start time and the end time. It 
	requires column format in form
	'b'	Byte	np.dtype('b')
	'i'	Signed integer	np.dtype('i4') == np.int32
	'u'	Unsigned integer	np.dtype('u1') == np.uint8
	'f'	Floating point	np.dtype('f8') == np.int64
	'c'	Complex floating point	np.dtype('c16') == np.complex128
	'S', 'a'	String	np.dtype('S5')
	'U'	Unicode string	np.dtype('U') == np.str_
	'V'	Raw data (void)	np.dtype('V') == np.void
	Example: 'i8' stands for int64.
	It also requires column_names to ease the access to the columns.

	'''

	def __init__(self, app, pipeline, column_formats, column_names, sessions_id=None, id=None, config=None):
		super().__init__(app, pipeline, id=id, config=config)
		svc = app.get_service("bspump.PumpService")
		if sessions_id is None:
			self.Sessions =  SessionMatrix(app, column_formats, column_names)
			svc.add_matrix(self.Sessions)
		else:
			self.Sessions = svc.locate_matrix(sessions_id)
	



		

	
	
	





	

