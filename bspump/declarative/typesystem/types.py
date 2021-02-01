import abc
import inspect

from . import traits


class TypeABC(abc.ABC):
	pass


class Type_si256(TypeABC):
	Traits = traits.TraitSignedInteger
	Name = 'si256'
	LLVM = 'i256'
	BitSize = 256
	Size = BitSize / 8


class Type_si128(TypeABC):
	Traits = traits.TraitSignedInteger
	Name = 'si128'
	LLVM = 'i128'
	BitSize = 128
	Size = BitSize / 8


class Type_si64(TypeABC):
	Traits = traits.TraitSignedInteger
	Name = 'si64'
	LLVM = 'i64'
	Alias = 'int'
	BitSize = 64
	Size = BitSize / 8


class Type_si32(TypeABC):
	Traits = traits.TraitSignedInteger
	Name = 'si32'
	LLVM = 'i32'
	BitSize = 32
	Size = BitSize / 8


class Type_si16(TypeABC):
	Traits = traits.TraitSignedInteger
	Name = 'si16'
	LLVM = 'i16'
	BitSize = 16
	Size = BitSize / 8


class Type_si8(TypeABC):
	Traits = traits.TraitSignedInteger
	Name = 'si8'
	LLVM = 'i8'
	BitSize = 8
	Size = BitSize / 8


class Type_ui256(TypeABC):
	Traits = traits.TraitUnsignedInteger
	Name = 'ui256'
	LLVM = 'i256'
	BitSize = 256
	Size = BitSize / 8


class Type_ui128(TypeABC):
	Traits = traits.TraitUnsignedInteger
	Name = 'ui128'
	LLVM = 'i128'
	BitSize = 128
	Size = BitSize / 8


class Type_ui64(TypeABC):
	Traits = traits.TraitUnsignedInteger
	Name = 'ui64'
	LLVM = 'i64'
	BitSize = 64
	Size = BitSize / 8


class Type_ui32(TypeABC):
	Traits = traits.TraitUnsignedInteger
	Name = 'ui32'
	LLVM = 'i32'
	BitSize = 32
	Size = BitSize / 8


class Type_ui16(TypeABC):
	Traits = traits.TraitUnsignedInteger
	Name = 'ui16'
	LLVM = 'i16'
	BitSize = 16
	Size = BitSize / 8


class Type_ui8(TypeABC):
	Traits = traits.TraitUnsignedInteger
	Name = 'ui8'
	LLVM = 'i8'
	BitSize = 8
	Size = BitSize / 8


class Type_ui1(TypeABC):
	Traits = traits.TraitUnsignedInteger | traits.TraitBoolean
	Name = 'ui1'
	LLVM = 'i1'
	Alias = 'bool'
	BitSize = 1
	Size = 1


class Type_si1(TypeABC):
	Traits = traits.TraitSignedInteger | traits.TraitBoolean
	Name = 'si1'
	LLVM = 'i1'
	BitSize = 1
	Size = 1


class Type_fp128(TypeABC):
	Traits = traits.TraitFloat
	Name = 'fp128'
	LLVM = 'fp128'
	BitSize = 128
	Size = BitSize / 8


class Type_fp64(TypeABC):
	Traits = traits.TraitFloat
	Name = 'fp64'
	LLVM = 'double'
	Alias = 'float'
	BitSize = 64
	Size = BitSize / 8


class Type_fp32(TypeABC):
	Traits = traits.TraitFloat
	Name = 'fp32'
	LLVM = 'float'
	BitSize = 32
	Size = BitSize / 8


class Type_fp16(TypeABC):
	Traits = traits.TraitFloat
	Name = 'fp16'
	LLVM = 'half'
	BitSize = 16
	Size = BitSize / 8


class Type_none(TypeABC):
	Traits = traits.TraitObject
	Name = 'none'
	Alias = 'NoneType'
	LLVM = r'%bs_type_none'


class Type_str(TypeABC):
	Traits = traits.TraitString
	Name = 'str'
	LLVM = r'%struct.bs_type_str*'


class Type_list(TypeABC):
	Traits = traits.TraitList
	Name = 'list'
	LLVM = r'%struct.bs_type_list*'


class Type_set(TypeABC):
	Traits = traits.TraitSet
	Name = 'set'
	LLVM = r'%struct.bs_type_set*'


def buildin_types(traits: frozenset = traits.TraitType) -> list:
	for o in globals().values():
		if inspect.isclass(o) \
			and issubclass(o, TypeABC) \
			and (o is not TypeABC) \
			and traits.issubset(o.Traits):
				yield o
