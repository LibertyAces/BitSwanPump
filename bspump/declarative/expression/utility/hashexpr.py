import xxhash

from ..value.valueexpr import VALUE
from ...abc import Expression

###


class HASH(Expression):

	Attributes = {
		"What": ["*"],
		"Seed": [
			'si64', 'si8', 'si16', 'si32',  # Those are not yet supported 'si128', 'si256',
			'ui8', 'ui16', 'ui32', 'ui64',  # Those are not yet supported 'ui128', 'ui256',
		],
		"Type": ["str"],  # And must be evaluated in compile type
	}


	def __init__(self, app, *, arg_what, arg_seed: int = 0, arg_type='xxhash64'):
		super().__init__(app)

		if isinstance(arg_type, Expression):
			self.Type = arg_type
		else:
			self.Type = VALUE(app, value=arg_type)
		arg_type = self.Type(None, None)
		assert(isinstance(arg_type, str))
		assert(arg_type in ('xxhash64'))

		if isinstance(arg_what, Expression):
			self.What = arg_what
		else:
			self.What = VALUE(app, value=arg_what)

		if isinstance(arg_seed, Expression):
			self.Seed = arg_seed
		else:
			self.Seed = VALUE(app, value=arg_seed)


	def initialize(self):
		outlet_type = self.What.get_outlet_type()
		self.Method = get_hash_method(self.Type, outlet_type)


	def __call__(self, context, event, *args, **kwargs):
		what = self.What(context, event, *args, **kwargs)
		seed = self.Seed(context, event, *args, **kwargs)
		return self.Method(what, seed)


	def get_outlet_type(self):
		return 'ui64'


def get_hash_method(hash_type, input_type):
	if hash_type == 'xxhash64':
		if input_type in (
			'int', 'si64', 'si8', 'si16', 'si32', 'si128', 'si256',
			'ui8', 'ui16', 'ui32', 'ui64', 'ui128', 'ui256'
		):
			# For integer, use the alternative hashing functions
			return hash_xxhash64_int

		elif input_type in ('str'):
			return hash_xxhash64_str

	raise NotImplementedError("Hashing for '{}' and '{}' is not yet implemented".format(hash_type, input_type))


def hash_xxhash64_str(what, seed):
	return xxhash.xxh64(what, seed=seed).intdigest()


def hash_xxhash64_int(what, seed):
	return (what ^ seed) & 0xFF_FF_FF_FF_FF_FF_FF_FF  # Limit to 64bits
