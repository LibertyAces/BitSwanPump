import numpy as np
import hashlib


class HyperLogLog(object):
	alphas = {16: 0.673, 32: 0.697, 64: 0.709}

	def __init__(self, m=64):
		self.num_bits = 32
		self.b = int(np.log2(m))
		self.bits = 2 ** self.num_bits
		self.m = m
		
		self.alpha = self.alphas.get(m)
		if self.alpha is None:
			raise "Incorrect m, it should be 16, 32 or 64"


	def add(self, value, array):
		#hashed_value = self._hash_data(value)
		hashed_value = value
		position = self._calculate_position(hashed_value)
		rho = self._calculate_rho(hashed_value)
		#print(hashed_value, position, rho, bin(hashed_value))
		array[position] = np.max([array[position], rho])


	def count(self, array): 
		z = self._calculate_z(array)
		e = self._calculate_e(z, array)
		return e


	def _hash_data(self, value):
		if isinstance(value, str):
			value = value.encode('utf8')

		#return int(hashlib.sha1(bytes(value)).hexdigest()[:16], 16) #whaaaaat
		return int(hashlib.sha1(bytes(value)).hexdigest(), 16) #whaaaaat


	def _calculate_z(self, array):
		twos = [0.5] * len(array)

		z = 1 / float(np.sum(np.power(twos, array)))
		#powers = np.power(twos, array)
		#z = 1 / float(np.sum(powers[powers != 1]))
		#print(np.power(twos, array), np.sum(np.power(twos, array)), z)
		return z


	def _calculate_e(self, z, array):

		e = z * self.alpha * self.m ** 2
		if e < 5/2 * self.m:
			v = self._get_zeros(array)
			if v != 0:
				e_star = self._linear_count(v)

			else:
				e_star = e
		
		elif e < 1/30 * 2 ** 32:
			e_star = e

		else:
			#print(e/(2 ** 32))
			e_star = -(2**32)* np.log(1 - e/(2**32))
		#print(z, e, e_star)
		return e_star


	def _get_zeros(self, array):
		return len(array[array == 0])


	def _linear_count(self, v):
		return self.m * np.log(self.m / v)


	def _calculate_position(self, hashed_value):
		'''
			takes b right bits.
		'''
		
		move = hashed_value & (self.bits - 1) >> (self.num_bits - self.b)
		#print(">>>>>", hashed_value, bin(hashed_value), move)
		return move

	def _calculate_rho(self, hashed_value):
		'''
			rho = 1 + <leftmost 1 position> 
		'''
		# SLOW:
		x = hashed_value
		pos = 32
		while x != 0:
			x = x >> 1 
			pos -= 1
		return pos + 1
		#return int(np.log2( hashed_value & -hashed_value) + 1)


	
