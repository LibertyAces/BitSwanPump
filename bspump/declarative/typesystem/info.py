import collections.abc

from .types import buildin_types
from . import traits


class _type_to_llvm(collections.abc.Mapping):
	'''
	This is a map of declarative type names into a LLVM types.
	'''

	def __init__(self):
		self.Types = dict((t.Name, t.LLVM) for t in buildin_types())

	def __getitem__(self, key):
		return self.Types.__getitem__(key)

	def __iter__(self):
		return self.Types.__iter__()

	def __len__(self):
		return self.Types.__len__()


type_to_llvm = _type_to_llvm()



class _type_size(collections.abc.Mapping):
	'''
	Size in bits of every integer type.
	'''

	def __init__(self, types):
		self.Types = dict((t.Name, t.BitSize) for t in types)

	def __getitem__(self, key):
		return self.Types.__getitem__(key)

	def __iter__(self):
		return self.Types.__iter__()

	def __len__(self):
		return self.Types.__len__()


int_type_size = _type_size(buildin_types(traits.TraitInteger))
float_type_size = _type_size(buildin_types(traits.TraitFloat))
scalar_type_size = _type_size(buildin_types(traits.TraitScalar))

scalar_types = frozenset(buildin_types(traits.TraitScalar))

name_to_type = dict((t.Name, t) for t in buildin_types())
