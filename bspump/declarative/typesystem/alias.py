from .types import buildin_types

# Type aliases are 'human friendly' or convinient names of types
# Each alias is to be resolved into a specific "canonical" type.
type_aliases = dict(
	(t.Alias, t) for t in buildin_types() if hasattr(t, 'Alias')
)


def unalias_type(type_or_alias: str) -> str:
	try:
		return type_aliases[type_or_alias]
	except KeyError:
		return type_or_alias
