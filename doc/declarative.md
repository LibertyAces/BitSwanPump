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

More at: [YAML specs, 10.1. Sequence Styles](https://yaml.org/spec/1.1/#id931088)



```
(a == 1) AND ((b == 2) OR (c == 3))
```

```
!AND
- !EQ
  - a
  - 1
- !OR
  - !EQ
    - b
    - 2
  - !EQ
    - c
    - 3
```



### Mappings

Example:

```
!DICT
with: {}
add:
  foo: green
  bar: dog
```

More at: [YAML specs, 10.2. Mapping Styles](https://yaml.org/spec/1.1/#id932806)


### Types

#### Boolean

* YAML: `!!bool`
* Values: `True`, `False`


#### Integers

* YAML: `!!int`
* Values: `0`, `-10000`, `-333`, ...


```
!!null
!!int	
!!float
!!binary
!!timestamp
!!omap
!!set
!!str
!!seq
!!map
```

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


### Comparisons `LT`, `LE`, `EQ`, `NE`, `GE`, `GT`

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


### `IF` statement

Type: _Mapping_.

```
!IF
is: <test>
then: <...>
else: <...>
```

### `WHEN` statement

It is a `IF` on steroid or also "case/switch". 

Type: _Sequence_.

```
!WHEN
- is: <test>
  then: <...>

- is: <test>
  then: <...>

- is: <test>
  then: <...>

- ...

- else: <...>
```

If `else` is not provided, then `WHEN` returns `False`.


### Dictionary manipulation `DICT`

Type: _Mapping_.

Create or update the dictionary.

```
!DICT
with: !EVENT
add:
	item1: foo
	item2: bar
	item3: ...
```


If `with` is not specified, the new dictionary will be created.  

Argument `add` (optional) specifies items to be added into the dictionary.

This is how to create the empty dictionary:

```
!DICT {}
```


### Dictionary `ITEM`

Get the item from a dictionary.

Type: _Mapping_ or _Scalar_.

```
!ITEM
with: !EVENT
item: foo
default: 0
```

```
!ITEM EVENT potatoes
```

_Note: Scalar form has some limitations (e.g no default value) but it is more compact._


### String tests "STARTSWITH", "ENDSWITH"

Type: _Mapping_.

```
!STARTSWITH
string: <...>
startswith: <...>
```

```
! ENDSWITH
string: <...>
endswith: <...>
```

### String transformations "LOWER", "UPPER"

Changes the string case.

Type: _Mapping_.

```
!LOWER
string: <...>
```

```
! UPPER
string: <...>
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

Search `value` forr `regex` with regular expressions groups.

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


### Access functions "EVENT", "CONTEXT"

Type: _Scalar_.

Returns the current event/context dictionary.


### Tuple "TUPLE"

Type: _Sequence_.

Transform input into a Python tuple.



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


### Test "INLIST"

Checks if value is in the list.

Type: _Mapping_.

```
!INLIST
value <...>
list: <...>
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

### Date/time to human readable string

Returns date/time in human readable format.

Type: _Mapping_.

```
!DATEFTM
datetime: <...>
format: <...>
````

The date is specified by `datetime`, which by default is current UTC time.

Format example: "%Y-%m-%d %H:%M:%S"



