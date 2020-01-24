import collections
import logging
import re

from ..abc.generator import Generator
from ..analyzer.sessionmatrix import SessionMatrix
from ..analyzer.timewindowmatrix import TimeWindowMatrix

#

L = logging.getLogger(__name__)

#


class TimeWindowMatrixExportTableauGenerator(Generator):

	async def generate(self, context, event, depth):
		assert(isinstance(event, TimeWindowMatrix))
		time_window_matrix = event

		for i in range(0, time_window_matrix.Array.shape[0]):
			row_id = time_window_matrix.get_row_name(i)
			if row_id is None:
				continue
			field_type = time_window_matrix.Array.dtype.subdtype[0].kind
			if field_type in ['f']:
				event_type = "double"
			elif field_type in ['i', 'u', 'b']:
				if re.search(r'timestamp', field_type) is not None:
					event_type = "datetime"
				else:
					event_type = "integer"

			elif field_type in ['U']:
				event_type = "unicodestring"
			else:
				L.warning("Incorrect type {}, skipping".format(field_type))
				break

			for j in range(0, time_window_matrix.Dimensions[0]):
				event = collections.OrderedDict()
				event['id'] = {"value": row_id, "type": "unicodestring"}
				value = time_window_matrix.Start + j * time_window_matrix.Resolution
				event['timestamp'] = {"value": value, "type": "datetime"}
				for k in range(0, time_window_matrix.Dimensions[1]):
					field_name = "value_{}".format(k)
					field_value = time_window_matrix.Array[i, j, k]
					event[field_name] = {"value": field_value, "type": event_type}

				self.Pipeline.inject(context, event, depth)


class SessionMatrixExportTableauGenerator(Generator):

	async def generate(self, context, event, depth):
		assert(isinstance(event, SessionMatrix))
		session_matrix = event

		for i in range(0, session_matrix.Array.shape[0]):
			event = collections.OrderedDict()
			row_id = session_matrix.get_row_name(i)
			if row_id is None:
				continue
			event['id'] = {"value": row_id, "type": "unicodestring"}
			for name in session_matrix.Array.dtype.names:
				if session_matrix.Array.dtype[name].shape == ():
					event[name] = {"value": None, "type": None}
					event[name]["value"] = session_matrix.Array[name][i]
					field_type = session_matrix.Array.dtype[name].kind
					if field_type in ['f']:
						event[name]["type"] = "double"
					elif field_type in ['i', 'u', 'b']:
						if re.search(r'timestamp', name) is not None:
							event[name]["type"] = "datetime"
						else:
							event[name]["type"] = "integer"

					elif field_type in ['U', 'S']:
						event[name]["type"] = "unicodestring"
					else:
						L.warning("Incorrect type {}, skipping".format(field_type))
						continue
				else:
					field_type = session_matrix.Array.dtype[name].subdtype[0].kind
					for j in range(0, session_matrix.Array.dtype[name].shape[0]):
						for k in range(0, session_matrix.Array.dtype[name].shape[1]):
							field_name = "{}_{}_{}".format(name, j, k)
							value = session_matrix.Array[name][i, j, k]
							event[field_name] = {"value": value, "type": None}

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
								L.warning("Incorrect type {}, skipping".format(field_type))
								continue
			self.Pipeline.inject(context, event, depth)
