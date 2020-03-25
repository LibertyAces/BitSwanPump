import numpy as np
import zlib


class HyperLogLog(object):
	'''
		This is the implementation of HyperLogLog++ algorithm,
		which estimates cardinality of the set with average 2%,
		described in http://algo.inria.fr/flajolet/Publications/FlFuGaMe07.pdf
		and https://storage.googleapis.com/pub-tools-public-publication-data/pdf/40671.pdf
	'''

	alphas = {16: 0.673, 32: 0.697, 64: 0.709}

	def __init__(self, m=2048):

		'''
			`m` is number of registers.
			`b` is the number of last bits of the value to take.
			`alpha` is the parameter from papers above.
		'''

		self.num_bits = 32
		self.b = int(np.ceil(np.log2(m)))
		self.max = 2 ** self.num_bits
		self.m = m
		
		if m >= 128:
			self.alpha = 0.7213 / (1 + 1.079 / m)
		else:
			self.alpha = self.alphas.get(m)

		if self.alpha is None:
			raise "Incorrect m, it should be 16, 32 or 64, or powers of 2 >= 128"



	def add(self, value, array):
		'''
			`value` might be string or number.
			`array` is a storage to 'add' the value.
		'''

		hashed_value = self.hash_data(value)
		position = self._calculate_position(hashed_value)
		rho = self._calculate_rho(hashed_value)
		array[position] = np.max([array[position], rho])


	def count(self, array):
		'''
			Count unique values in array.
		'''

		z = self._calculate_z(array)
		e = self._calculate_e(z, array)
		return int(e)


	def hash_data(self, value):
		'''
			Override it, if you want to use different hash.
			Hash must be 32bit and fast (don't use cryptographic hashes then)
		'''

		if not isinstance(value, str):
			value = str(value)

		value = value.encode('utf8')
		return zlib.crc32(value)


	def _calculate_z(self, array):
		twos = [0.5] * len(array)
		z = 1 / float(np.sum(np.power(twos, array)))
		return z


	def _calculate_e(self, z, array):
		e = z * self.alpha * self.m ** 2
		if e < 5 / 2 * self.m:
			v = self._get_zeros(array)
			if v != 0:
				e_star = float(self._linear_count(v))

			else:
				e_star = e

		elif e < 1 / 30 * self.max:
			e_star = e

		else:
			e_star = -self.max * float(np.log(1 - e / self.max))
		return e_star


	def _get_zeros(self, array):
		return len(array[array == 0])


	def _linear_count(self, v):
		return self.m * np.log(self.m / v)


	def _calculate_position(self, hashed_value):
		'''
			takes b right bits.
		'''
		move = hashed_value & (self.max - 1) >> (self.num_bits - self.b)
		return move


	def _calculate_rho(self, hashed_value):
		'''
			rho = 1 + <leftmost 1 position>
		'''
		# SLOW: TODO: find the way to do it better
		x = hashed_value
		pos = self.num_bits
		while x > 1:
			x = x >> 1
			pos -= 1

		return pos
