
TraitType = frozenset({'Type'})

TraitScalar = frozenset({'Scalar'}) | TraitType
TraitNumber = frozenset({'Number'}) | TraitScalar
TraitInteger = frozenset({'Integer'}) | TraitNumber
TraitSignedInteger = frozenset({'SignedInteger'}) | TraitInteger
TraitUnsignedInteger = frozenset({'UnsignedInteger'}) | TraitInteger

TraitFloat = frozenset({'Float'}) | TraitNumber

TraitBoolean = frozenset({'Boolean'}) | TraitScalar

TraitObject = frozenset({'Object'}) | TraitType

TraitCollection = frozenset({'Collection', 'Sized', 'Iterable', 'Container'}) | TraitObject

TraitSet = frozenset({'Set'}) | TraitCollection
TraitList = frozenset({'List', 'Reversible'}) | TraitCollection
TraitString = frozenset({'String'}) | TraitList
