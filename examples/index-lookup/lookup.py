import bspump
import bspump.lookup
import logging
import pandas as pd
import numpy as np

##

L = logging.getLogger(__name__)

##

class MyIndexLookup(bspump.lookup.IndexLookup):
	ConfigDefaults = {
		'delimiter' : ',',
		'path': '',
	}

	async def load(self):
		print('loading!')
		path = self.Config['path']
		if path == '':
			L.warn('Path is empty!')
			raise 

		df = pd.read_csv(path, delimiter=self.Config['delimiter'])
		df['startdate'] = pd.to_datetime(df['startdate'])
		df['enddate'] = pd.to_datetime(df['enddate'])
		df['ts_start'] =  df.startdate.values.astype(np.int64) // 10 ** 9
		df['ts_end'] =  df.enddate.values.astype(np.int64) // 10 ** 9
		df.drop(['startdate', 'enddate', 'epizodename'], axis=1, inplace=True)
		self.Matrix.Array = np.array(df.to_records())
		self.Matrix.DType = self.Matrix.Array.dtype.descr
		for i in range(self.Matrix.Array.shape[0]):
			value = int(self.Matrix.Array[i]['epgid'])
			self.Matrix.I2NMap[i] = value
			self.Matrix.N2IMap[value] = i

		self.add_bitmap_index('channelid')
		return True


	def search(self, condition):
		x = np.where(condition)
		if len(x[0]) == 0:
			return None
		
		return np.asscalar(self.Matrix.Array[x[0]]['epgid'])

