import collections
import logging

from ..abc.generator import Generator
from ..analyzer.sessionmatrix import SessionMatrix
from ..analyzer.timewindowmatrix import TimeWindowMatrix


L = logging.getLogger(__name__)


class TimeWindowMatrixExportCSVGenerator(Generator):

	def process(self, context, event):
		assert(isinstance(event, TimeWindowMatrix))

		def generate(time_window_matrix):
			for i in range(time_window_matrix.Array.shape[0]):
				row_id = time_window_matrix.get_row_name(i)
				if row_id is None:
					continue

				for j in range(0, time_window_matrix.Dimensions[0]):
					event = collections.OrderedDict()
					event['id'] = row_id
					event['timestamp'] = time_window_matrix.Start + j * time_window_matrix.Resolution
					for k in range(0, time_window_matrix.Dimensions[1]):
						field_name = "value_{}".format(k)
						event[field_name] = time_window_matrix.Array[i, j, k]

					yield event

		return generate(event)



class SessionMatrixExportCSVGenerator(Generator):

	def process(self, context, event):
		assert(isinstance(event, SessionMatrix))

		def generate(session_matrix):
			for i in range(0, session_matrix.Array.shape[0]):
				event = collections.OrderedDict()
				row_id = session_matrix.get_row_name(i)
				if row_id is None:
					continue
				event['id'] = row_id
				for name in session_matrix.Array.dtype.names:
					if session_matrix.Array.dtype[name].shape == ():
						event[name] = session_matrix.Array[name][i]
					else:
						for j in range(0, session_matrix.Array.dtype[name].shape[0]):
							for k in range(0, session_matrix.Array.dtype[name].shape[1]):
								field_name = "{}_{}_{}".format(name, j, k)
								if session_matrix.Array.dtype[name].subdtype[0].kind in ['f', 'u', 'i', 'b']:
									value = "{0:.10f}".format(session_matrix.Array[name][i, j, k])
								else:
									value = session_matrix.Array[name][i, j, k]

								event[field_name] = value

				yield event

		return generate(event)
