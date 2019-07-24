import time
import logging
import numpy as np
import re
import collections

import asab

from .analyzer import Analyzer
from .sessionmatrix import SessionMatrix

###

L = logging.getLogger(__name__)

###


class SessionAnalyzer(Analyzer):
	'''
		This is the analyzer for events with multiple different dimensions.

		`SessionAnalyzer` operates over the `SessionMatrix` object.
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
		Important! However it is possible to use all these letters, it is recommeded to use only 'i' for integers, 'f' for
		floats, 'U' for strings. Anything else might cause problems in serialization. 
		It is possible to create a matrix with elements of specified format. The tuple with number of dimensions should 
		stand before the letter.
		Example: '(6, 3)i8' will create the matrix with n rows, 6 columns and 3 third dimensions with integer elements.
		`column_names` is an array with names of each column, with the same length as `column_formats`.
		`matrix_id` is an id of `SessionMatrix` object defined alternatively.

	'''

	def __init__(self, app, pipeline, column_formats, column_names, analyze_on_clock=False, matrix_id=None, id=None, config=None):
		super().__init__(app, pipeline, analyze_on_clock=analyze_on_clock, id=id, config=config)
		svc = app.get_service("bspump.PumpService")
		if matrix_id is None:
			s_id = self.Id + "Matrix"
			self.Sessions =  SessionMatrix(app, column_formats, column_names, id=s_id)
			svc.add_matrix(self.Sessions)
		else:
			self.Sessions = svc.locate_matrix(matrix_id)

		# self.Matrix = self.Sessions.Matrix #alias


	async def export_to_csv(self, internal_source):
		'''
		| row_id | column_0 | column_1 | ... | column_n |
		'''
		if internal_source is None:
			L.warn("Internal source is None, are you sure you called locate?")
			return
		
		for i in range(0, self.Sessions.Matrix.shape[0]):
			event = collections.OrderedDict()
			row_id = self.Sessions.get_row_id(i)
			event['id'] = row_id
			for name in self.Sessions.Matrix.dtype.names:
				if self.Sessions.Matrix.dtype[name].shape == ():
					event[name] = self.Sessions.Matrix[name][i]
				else:
					# print(self.Matrix.dtype[name].shape)
					for j in range(0, self.Sessions.Matrix.dtype[name].shape[0]):
						for k in range(0, self.Sessions.Matrix.dtype[name].shape[1]):
							field_name = "{}_{}_{}".format(name, j, k)
							if self.Sessions.Matrix.dtype[name].subdtype[0].kind in ['f', 'u', 'i', 'b']:
								value =  "{0:.10f}".format(self.Sessions.Matrix[name][i, j, k])
							else:
								value = self.Sessions.Matrix[name][i, j, k]
						
							event[field_name] = value
			await internal_source.put_async({}, event)


	async def export_to_tableau(self, internal_source):
		if internal_source is None:
			L.warn("Internal source is None, are you sure you called locate?")
			return
			
		for i in range(0, self.Sessions.Matrix.shape[0]):
			event = collections.OrderedDict()
			row_id = self.Sessions.get_row_id(i)
			event['id'] = {"value":row_id, "type": "unicodestring"}
			for name in self.Sessions.Matrix.dtype.names:
				if self.Sessions.Matrix.dtype[name].shape == ():
					event[name] = {"value":None, "type": None}
					event[name]["value"] = self.Sessions.Matrix[name][i]
					field_type = self.Sessions.Matrix.dtype[name].kind
					if field_type in ['f']:
						event[field_name]["type"] = "double"
					elif field_type in ['i', 'u', 'b']:
						if re.search(r'timestamp', name) is not None:
							event[name]["type"] = "datetime"
						else:
							event[name]["type"] = "integer"
					
					elif field_type in ['U', 'S']: 
						event[name]["type"] = "unicodestring"
					else:
						L.warn("Incorrect type {}, skipping".format(field_type))
						continue
				else:
					field_type = self.Sessions.Matrix.dtype[name].subdtype[0].kind
					for j in range(0, self.Sessions.Matrix.dtype[name].shape[0]):
						for k in range(0, self.Sessions.Matrix.dtype[name].shape[1]):
							field_name = "{}_{}_{}".format(name, j, k)
							value = self.Sessions.Matrix[name][i, j, k]
							event[field_name] = {"value":value, "type": None}
				
							if field_type in ['f']:
								event[field_name]["type"] = "double"
							elif field_type in ['i', 'u', 'b']:
								if re.search(r'timestamp', name) is not None:
									event[field_name]["type"] = "datetime"
								else:
									event[field_name]["type"] = "integer"
							
							elif field_type in ['U', 'S']: 
								event[field_name]["type"] = "unicodestring"
							else:
								L.warn("Incorrect type {}, skipping".format(field_type))
								continue
							
				await internal_source.put_async({}, event)







	

