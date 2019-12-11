import logging

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

	def __init__(self, app, pipeline, matrix_id=None, dtype='float_', analyze_on_clock=False, id=None, config=None):
		super().__init__(app, pipeline, analyze_on_clock=analyze_on_clock, id=id, config=config)
		svc = app.get_service("bspump.PumpService")
		if matrix_id is None:
			s_id = self.Id + "Matrix"
			self.Sessions = SessionMatrix(app, dtype, id=s_id)
			svc.add_matrix(self.Sessions)
		else:
			self.Sessions = svc.locate_matrix(matrix_id)
