# BSPump declarations


## Basics

* YAML 1.1
* Functions are YAML _tags_ (`!TAG`).


## Syntax

### Scalars

Example:  

```
!ITEM EVENT potatoes
```

More at: [YAML specs, Chapter 9. Scalar Styles](https://yaml.org/spec/1.1/#id903915)


### Sequences

Example:

```
!ADD  
- 1  
- 2  
- 3  
```

Short form example:

```
!ADD  [1, 2, 3]  
```


More at: [YAML specs, 10.1. Sequence Styles](https://yaml.org/spec/1.1/#id931088)


### Mappings

Example:

```
!DICT
  foo: green
  bar: dog
```

Short form example:

```
!DICT { }
```


More at: [YAML specs, 10.2. Mapping Styles](https://yaml.org/spec/1.1/#id932806)


### Types


#### Null

* YAML: `!!null`
* Value: `None`


#### Boolean

* YAML: `!!bool`
* Values: `True`, `False`


#### Integer

* YAML: `!!int`
* Values: `0`, `-10000`, `-333`, ...

#### Float

* YAML: `!!float`
* Values: `1.23`, ....

#### Complex types

* `!!binary`
* `!!timestamp`
* `!!omap`
* `!!set`
* `!!str`
* `!!seq`
* `!!map`


## Comments

```
	# This is a comment.
```

## Expressions


### Arithmetics : `ADD`, `DIV`, `MUL`, `SUB`

Type: _Sequence_.

```
---
!ADD
- 1
- 2
- 3
```


### Logicals `AND`, `OR`, `NOT`

Type: _Sequence_.

```
---
!OR
- !ITEM EVENT isLocal
- !ITEM EVENT isRemote
- !ITEM EVENT isDangerous
```


### Comparisons `LT`, `LE`, `EQ`, `NE`, `GE`, `GT`, `IS`, `ISNOT`

Type: _Sequence_.

Example of a `Event.count == 3` check:  

```
! EQ
- !ITEM EVENT count
- 3
```


Example of a range `2 < Event.count < 5` check:  

```
!LT
- 2
- !ITEM EVENT count
- 5
```

Example of is `Event.user1 is Event.user2 is Event.user3` check:

```
!IS
- !ITEM EVENT user1
- !ITEM EVENT user2
- !ITEM EVENT user3
```


### `IF` statement

Type: _Mapping_.

```
!IF
test: <expression>
then: <expression>
else: <expression>
```

### `WHEN` statement

It is a `IF` on steroid or also "case/switch". 

Type: _Sequence_.

```
!WHEN
- test: <expression>
  then: <expression>

- test: <expression>
  then: <expression>

- test: <expression>
  then: <expression>

- ...

- else: <expression>
```

If `else` is not provided, then `WHEN` returns `False`.


### Data Structure: Dictionary `DICT`

Type: _Mapping_.

Create or update the dictionary.

```
!DICT
with: !EVENT
set:
	item1: foo
	item2: bar
	item3: ...
del:
  - item4
  - item5
add:
  item6: 1
```


If `with` is not specified, the new dictionary will be created.  

Argument `set` (optional) specifies items to be set (added, updated) to the dictionary.

Argument `del` (optional) specifies items to be removed from a dictionary.

Argument `add` (optional) is similar to `set` but the operator `+=` is applied. The item must exist.

This is how to create the empty dictionary:

```
!DICT {}
```


### Dictionary `ITEM`

Get the item from a dictionary, tuple, list, etc.

Type: _Mapping_ or _Scalar_.

```
!ITEM
with: <expression>
item: foo
default: 0
```

```
!ITEM EVENT potatoes
```

_Note: Scalar form has some limitations (e.g no default value) but it is more compact._


### Data Structure: Tuple `TUPLE`

Type: _Sequence_.

Create the tuple.

```
!TUPLE
- first
- second
- third
```

Short form:

```
!TUPLE [first, second, third]
```


### String tests "STARTSWITH", "ENDSWITH", "CONTAINS"

Type: _Mapping_.

```
!STARTSWITH
value: <...>
prefix: <...>
```

```
!ENDSWITH
value: <...>
postfix: <...>
```

```
!CONTAINS
string: <...>
contains: <...>
```

### String transformations "LOWER", "UPPER", "JOIN", "SUBSTRING"

Changes the string case.

Type: _Mapping_.

```
!LOWER
value: <...>
```

```
!UPPER
value: <...>
```

```
!JOIN
items:
	-<...>
	-<...>
char: - (default is space " ")
```

```
!SUBSTRING
value: <...>
from: (int, default 0)
to: (int, default -1)
```

### Regular expression "REGEX"

Checks if `value` matches with the `regex`, returns `hit` / `miss` respectively.

Type: _Mapping_.

```
!REGEX
regex: <...>
value: <...>
hit: <...|default True>
miss: <...|default False>
```
Note: Uses Python regular expression.

### Regular expression "REGEX_PARSE"

Search `value` for `regex` with regular expressions groups.

Type: _Mapping_.

```
!REGEX_PARSE
regex: '^(\w+)\s+(\w+)\s+(frank|march)?'
items: [Foo, Bar,  <...>]
value: <...>
```

If nothing is found `miss` is returned.
Otherwise, groups are returned in as a list.

If `items ` are provided, the groups are mapped to provided `items` and a dictionary is returned.

### Regular expression "REGEX_REPLACE"

Searches for `regex_search` in `value` and replaces leftmost occurrence with `regex_replace`.

```
!REGEX_REPLACE
regex_search: '^(\w+)\s+(\w+)\s+(frank|march)?'
regex_replace: '^(\w+)\s+(\w+)\s+(frank|march)?'
value: <...>
```

If nothing is found `miss` is returned.
Otherwise, groups are returned in as a list.

If `items ` are provided, the groups are mapped to provided `items` and a dictionary is returned.


### Access functions "EVENT", "CONTEXT", "KWARGS"

Type: _Scalar_.

Returns the current event/context/keyword arguments dictionary.


### Scalar function "VALUE"

Type: _Scalar_.

Returns the value of the scalar.
The usage of this expression is typically advanced or internal.


### Lookup "LOOKUP"

Obtains value from `lookup` (id of the lookup) using `key`.

Type: _Mapping_.

```
!LOOKUP
lookup: <...>
key: <...>
```

### Utility

#### Utility "MAP"

Checks if `value` exists in the provided key-value map. If so, it returns the mapped value, otherwise
returns default value specified in the `else` branch.

```
!MAP
value: !ITEM EVENT potatoes
map:
	7: only seven
	20: twenty
	12: twelve
	10: enough to join the potato throwing competition
else:
	no right amount of potatoes found
```

#### Utility "CAST"

Casts specified `value` to `type`, which can be int, float, str, list and dict.

```
!CAST
value: !ITEM EVENT carrots
type: int
default: 0
```

`default` is returned when cast fails, it is optional, with default value of `None`.



### Test "IN"

Checks if `expression` (list, tuple, dictionary, etc.) contains the result `is` expression. 

Type: _Mapping_.

```
!IN
expr: <...>
is: <...>
```


### Test "INSUBNET"

Checks if value (IP Address) is inside the given subnet.

```
!INSUBNET
value <...>
subnet: <...>
```


### Date/time functions

### `NOW`

Get a current UTC date and time.

Type: _Mapping_.

```
!NOW
```

### Date/time to human readable string `DATETIME_FORMAT`

Returns date/time in human readable format.

Type: _Mapping_.

```
!DATETIME_FORMAT
value: <... of datetime, int or float>
format: <...>
````

The date/time is specified by `value`, which by default is current UTC time.  
`int` or `float` values are considered as a UNIX timestamps.

Format example: "%Y-%m-%d %H:%M:%S"


### Debug output `DEBUG`

Print the content of the `arg` onto console and pass that unchanged.

```
!DEBUG
arg: !ITEM EVENT potatoes
```
