import json
import logging

import numpy as np

import asab
from ..abc.lookup import Lookup
from ..analyzer.sessionmatrix import SessionMatrix

###

L = logging.getLogger(__name__)

###


class MatrixLookup(Lookup):
	'''
		Numpy Lookup
	'''

	ConfigDefaults = {
		"update_period": 5,
	}

	def __init__(self, app, matrix_id=None, dtype='float_', on_clock_update=False, id=None, config=None, lazy=False):

		super().__init__(app, id=id, config=config, lazy=lazy)
		self.Indexes = {}

		svc = app.get_service("bspump.PumpService")
		if matrix_id is None:
			s_id = self.Id + "Matrix"
			self.Matrix = SessionMatrix(app, dtype, id=s_id)
			svc.add_matrix(self.Matrix)
		else:
			self.Matrix = svc.locate_matrix(matrix_id)

		self.MatrixPubSub = None
		self.Timer = None

		self.Target = None

		if self.is_master():
			if on_clock_update:
				self.UpdatePeriod = float(self.Config['update_period'])
				self.Timer = asab.Timer(app, self._on_clock_tick, autorestart=True)
				self.Timer.start(self.UpdatePeriod)

			else:
				self.MatrixPubSub = self.Matrix.PubSub
				self.MatrixPubSub.subscribe("Matrix changed!", self._on_matrix_changed)



	async def _on_matrix_changed(self, message):
		self.update_indexes()


	async def _on_clock_tick(self):
		self.update_indexes()


	def update_indexes(self):
		for index in self.Indexes:
			self.Indexes[index].update(self.Matrix)


	def search(self, condition, target_column):
		'''
			Default search, override if optimized with indexes
		'''
		x = np.where(condition)
		if len(x[0]) == 0:

			return None

		return np.asscalar(self.Matrix.Array[x[0][0]][target_column])


	def serialize(self):
		serialized = {}
		serialized['Matrix'] = self.Matrix.serialize()
		serialized['Indexes'] = {}
		for index in self.Indexes:
			serialized["Indexes"][index] = self.Indexes[index].serialize()

		return (json.dumps(serialized)).encode('utf-8')


	def deserialize(self, data_json):
		data = json.loads(data_json.decode('utf-8'))
		self.Matrix.deserialize(data['Matrix'])
		indexes = data.get("Indexes", {})
		for index in indexes:
			self.Indexes[index].deserialize(indexes[index])


	def rest_get(self):
		rest = super().rest_get()
		rest['Indexes'] = {}
		for index in self.Indexes:
			rest['Indexes'][index] = self.Indexes[index].serialize()
		rest['Matrix'] = self.Matrix.serialize()
		return rest


	def create_index(self, index_class, *args, **kwarg):
		new_index = index_class(*args, **kwarg)
		index_id = new_index.Id
		self.Indexes[index_id] = new_index
		return new_index
