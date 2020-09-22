---
layout: default
title: LogMan.io documentation
header: Declarative Doc
sidebar: logmanio
---

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


### Logicals `AND`, `OR`

Type: _Sequence_.

```
---
!OR
- !ITEM EVENT isLocal
- !ITEM EVENT isRemote
- !ITEM EVENT isDangerous
```

### Logical negation `NOT`

Type: _Mapping_.

```
---
!NOT
what: <expression>
```


### Comparisons `LT`, `LE`, `EQ`, `NE`, `GE`, `GT`, `IS`, `ISNOT`

Type: _Sequence_.

Example of a `Event.count == 3` check:  

```
!EQ
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


Example of `!WHEN` use for exact match, range match and set match:

```
---
!WHEN

# Exact value match
- test:
    !EQ
    - !ITEM EVENT key
    - 34
  then:
    "Thirty four"

# Range match
- test:
    !LT
    - 40
    - !ITEM EVENT key
    - 50
  then:
    "fourty to fifty (exclusive)"

# In-set match
- test:
    !IN
    what: !ITEM EVENT key
    where:
      - 75
      - 77
      - 79
  then:
    "seventy five, seven, nine"


- else:
    "Unknown"
```


### `FOR` statement

Apply `do` for each item.

Type: _Sequence_.

```
!FOR
  each: !ARG
  do: <...>
```


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

unset:
  - item4
  - item5

add:
  item6: 1

modify:
	item7:
	  !LOWER:
    what: !ARG

update:
	!DICT

mandatory:
	- item1
	- item2
	- item6
```

If `with` is not specified, the new dictionary will be created.

If expression in `with` returns None, then the result of the entire `!DICT` expression is also None.

Argument `set` (optional) specifies items to be set (added, updated) to the dictionary.
If the value of the item to be set is `None`, then the item is not added/updated to the dictionary.

Argument `unset` (optional) specifies items to be removed from a dictionary.

Argument `add` (optional) is similar to `set` but the operator `+=` is applied. The item must exist.

Argument `modify` (optional) is similar to `set` but the item must exist and it is passed to a subsequent expression as a `!ARG` (to _modify_ it). It the item doesn't exists, the entry is skipped.

Argument `update` (optional) allows to update the dictionary with items from another dictionary.
The `ARG` contains a current value of the dictionary.

Argument `mandatory` (optional) allows to specify a list of mandatory attributes, that must be set
after all other operations are performed. If one of the mandatory fields is missing, None is returned.

```
- !DICT
  set:
    include: sub1

  update:
    !MAP
      what: !ITEM ARG include
      in:
        'sub1': !INCLUDE sub1
        'sub2': !INCLUDE sub2
```

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

### Parse a dictionary `!DICT.PARSE`

Type: _Mapping_.

```
!DICT.PARSE
what: ...
type: kvs
set: ...
unset: ...
update: ...
```

Parse `what` input (string) into a dictionary.
`what` can be of various key/value formats, specified by `type`.

`set`, `unset` and `update` arguments are also available, see `!DICT` chapter for more details.


#### Simple key/value format with space separation `kvdqs`

Type: `kvs`

Example: 

```
key1=value1 key2=value2 key3=value3
```

#### Key/value format with values in double quotes and with space separation

Type: `kvdqs`

Example: 

```
key1="value1" key2="value2" key3="value\"3\"" key3="value four" 
```

#### URL Query string

Type: `qs`

Example: 

```
first=this+is+a+field&second=was+it+clear+%28already%29%3F
```



### String tests "STARTSWITH", "ENDSWITH", "CONTAINS"

Type: _Mapping_.

```
!STARTSWITH
what: <...>
prefix: <...>
```

```
!ENDSWITH
what: <...>
postfix: <...>
```

```
!CONTAINS
what: <...>
substring: <...>
```

### String cut "CUT"

Type: _Mapping_.

```
!CUT
what: <...>
delimiter: ','
field: 1
```

Cut the `what` string by a `delimiter` and return the piece identified by `field` index (starts with 0).


### String transformations "LOWER", "UPPER","SUBSTRING"

Changes the string case.

Type: _Mapping_.

```
!LOWER
what: <...>
```

```
!UPPER
what: <...>
```

```
!SUBSTRING
what: <...>
from: (int, default 0)
to: (int, default -1)
```


### Join items in a string "!JOIN"

```
!JOIN
items:
  - <...>
  - <...>
delimiter: '-'
miss: ''
```

Default `delimiter` is space (" ").

If the item is `None`, then the value of `miss` parameter is used, by default it is empty string ''.
If `miss` is `!!null` (`None`) and  any of `items` is `None`, the result of the whole join is `None`.


### Regular expression "REGEX"

Checks if `what` matches with the `regex`, returns `hit` / `miss` respectively.

Type: _Mapping_.

```
!REGEX
what: <...>
regex: <...>
hit: <...|default True>
miss: <...|default False>
```
Note: Uses Python regular expression.


### Parsing by regular expression "REGEX.PARSE"

Search `what` for `regex` with regular expressions groups.

Type: _Mapping_.

```
!REGEX.PARSE
what: <...>
regex: '^(\w+)\s+(\w+)\s+(frank|march)?'
items: [Foo, Bar,  <...>]
miss: Missed :-(
set:
	item1: foo
	item2: bar
unset:
  - item1
update:
  item2: ...
```

Alternatively, with linear block parsing,
there is no need to escape the `regex` string:

If nothing is found `miss` is returned.
Otherwise, groups are returned in as a list.

If `items ` are provided, the groups are mapped to provided `items` and a dictionary is returned.

Entries in `items` can have following forms:

 * Simple string entry, then the value of the regex group is used directly
 * Expression, then the value of the regex group is passed in the expression as `!ARG` and the result of the expression is then used in the dictionary
 * List of expressions, similar to the previous but the list is iterated till the given expression returns non-None result, then the value is used in the dictionary

 Value `None` is skipped and not set to the dictionary.

 Example of three forms:

 ```
!REGEX.PARSE
what: "foo 123 a.b.c.d"
regex: '^(\w+)\s+(\d+)\s+([\w.]+)$'
items:
  - SimpleEntry
  - Expression:
    !CAST
    what: !ARG
    type: int
  - ListOfExpressions:
    - !REGEX.PARSE
      regex: '^(\d)$'
      what: !ARG
    - !REGEX.PARSE
      regex: '^(\s\.\s\.\s\.\s)$'
      what: !ARG
 ```

The argument `set` (optional) allows to add/update additional items into a result dictionary.
In the `set` part, the intermediate form of the result is available as `ARG`.
If `None` is returned, the result is not modified.

```
---
!REGEX.PARSE
what: 'foo 123 bar'
regex: '^(\w+)\s+(\d+)\s+(\w+)$'

items:
  - first
  - second
  - third

set:
  third:
    !ADD
    - !ITEM ARG third
    - ' with postfix'
```

`unset` and `update` arguments are also available, see `!DICT` chapter for more details.

More complex parsing:

```
!REGEX.PARSE
  what: !EVENT
  regex: '^(\w+)\s(\w+)\s(.*)$'
  items:
    - item1
    - item2
    - .body

  update:
    !MAP
      what: !ITEM ARG item2
      in:
        'sub1': !INCLUDE subparser1
        'sub2': !INCLUDE subparser2

  unset:
    - .body
```

And the `subparser1.yaml` example:

```
!REGEX.PARSE
  what: !ITEM ARG .body
  regex: '^(\w+)\s(.*)$'
  items:
        - word1
        - word2
```

In order to escape quote character `'` in `regex` attribute,
double the character `''`.
The expression then looks as follows:

```
!REGEX.PARSE
  what: !ITEM ARG .body
  regex: '^(\w+)''\s(.*)$'
  items:
        - word1
        - word2
```

Or with linear block parsing:

```
!REGEX.PARSE
  what: !ITEM ARG .body
  regex: >
	'^(\w+)'\s(.*)$'
  items:
        - word1
        - word2
```

Double quotes are escaped with slash in the beginning.

### Regular expression "REGEX.REPLACE"

Searches for `regex` in `what` and replaces leftmost occurrence with `replace`.

Type: _Mapping_.


See Python documentation of `re.sub()` for more details.

```
!REGEX.REPLACE
what: <... of type string>
regex: '^(\w+)\s+(\w+)\s+(frank|march)?'
replace: <... of type string>
```


### Regular expression "REGEX.SPLIT"

Split `what` by `regex`.

Type: _Mapping_.

```
!REGEX.SPLIT
what: <...>
regex: '^(\w+)\s+(\w+)\s+(frank|march)?'
max: 2
```

Optional value `max` specifies maximum splits, by default there is no maximum limit.


### Access functions "EVENT", "CONTEXT", "KWARGS"

Type: _Scalar_.

Returns the current event/context/keyword arguments dictionary.


### Scalar function "VALUE"

Type: _Scalar_.

Returns the value of the scalar.
The usage of this expression is typically advanced or internal.


### Lookups

#### Obtain value from a lookup "LOOKUP.GET"

Obtains value from a lookup specified by `in` (id of the lookup) using `what` as a key.

Type: _Mapping_.

```
!LOOKUP.GET
what: <...>
in: <...>
```
#### Check if a lookup contains the value "LOOKUP.CONTAINS"

Returns `True` is a lookup specified by `in` (id of the lookup) contains a key `what`.
If not, then `False` is returned. 

Type: _Mapping_.

```
!LOOKUP.CONTAINS
what: <...>
in: <...>
```


### Utility

#### Utility "MAP"

Type: _Mapping_

Checks if `what` exists in the provided key-value map. If so, it returns the mapped value, otherwise returns default value specified in the `else` branch.

```
!MAP
what: !ITEM EVENT potatoes

in:
	7: only seven
	20: twenty
	12: twelve
	10: enough to join the potato throwing competition

else:
	no right amount of potatoes found
```

For more complex tasks that for example include range check, check also a `!WHEN` expression.

_Note:_ the `!MAP` expression can be combined with `!INCLUDE` statement for a faster evaluation (based on `what`) and a structured declarations.


#### Utility "FIRST"

Type: _SEQUENCE_

```
!FIRST
- <expression>
- <expression>
- <expression>
...
```

Iterate thru expression (top down), if the expression return non-null (`None`) result, stop iteration and return that value. Otherwise continue to the next expression.

It returns `None` when end of the list is reached.


#### Utility "CAST"

Type: _Mapping_ and _Scalar_.

Casts specified `what` to `type`, which can be int, float, str, list and dict.

```
!CAST
what: !ITEM EVENT carrots
type: int
default: 0
```

`default` is returned when cast fails, it is optional, with default value of `None`.


There is also a scalar version:

```
!CAST int
```

It only allows to specify the `type` argument, the value is taken from `!ARG`.


### Test "IN"

Checks if `where` (list, tuple, dictionary, etc.) contains the result `what` expression. 

Type: _Mapping_.

```
!IN
what: <...>
where: <...>
```

### IP Address functions

IP address is internally represented as IPv6 128-bit integer.
IPv4 are mapped into the IPv4 space as prescribed by [RFC 4291 section 2.5.5.2. IPv4-Mapped IPv6 Address](https://tools.ietf.org/html/rfc4291#section-2.5.5.2).

### `IP.PARSE`

Parses string, hex number or decimal number to internal IP address integer representation.

```
!IP.PARSE <...>
```

### `IP.FORMAT`

Convert IP address to its string representation.

```
!IP.FORMAT
what: <...>
format: auto|ipv4|ipv6
```


### `IP.INSUBNET`

Checks if value (IP Address) is inside the given subnet, which may be a provided list.

Returns `True` / `False` (boolean).

```
!IP.INSUBNET
what: <...>
subnet: [<...>]
```


### Date/time functions

### `NOW`

Get a current UTC date and time.

Type: _Mapping_.

```
!NOW
```

### Date/time to human readable string `DATETIME.FORMAT`

Returns date/time in human readable format.

Type: _Mapping_.

```
!DATETIME.FORMAT
with: <... of datetime, int or float>
format: <...>
```

The date/time is specified by `with`, which by default is current UTC time. The default value of the `with` is the current data and time.

`int` or `float` values are considered as a UNIX timestamps.

Format example: "%Y-%m-%d %H:%M:%S"


### Date/time parse `DATETIME.PARSE`

Parse the date/time from a string

Type: _Mapping_.

```
!DATETIME.PARSE
what: <... of datetime, int or float>
format: <...>
timezone: Europe/Prague
flags: Y
```

The date/time is specified by `what`.
  
`int` or `float` values are considered as a UNIX timestamps.

Format example: "%Y-%m-%d %H:%M:%S"

Special format shortcuts:

 * `RFC3339` Format according to RFC 3339 / Date and Time on the Internet: Timestamps

`timezone` is optional, if not provided, UTC time is assumed.
The details about format of timezone can be found at http://pytz.sourceforge.net/

String `flags` specifies special conditions to be applied:

* `Y`: Use a current year, suited for parsing incomplete dates such as `17 Mar`.


### Access elements of Date/time  `DATETIME.GET`

Get the value of particular components of the date/time, such month, year or hour.

Type: _Mapping_.

```
!DATETIME.GET
with: <... of datetime, int or float>
what: [year|month|day|hour|minute|second|microsecond|timestamp|
timezone: Europe/Prague
weekday|isoweekday]
```

`timezone` is optional, if not provided, UTC time is assumed.
The details about format of timezone can be found at http://pytz.sourceforge.net/


### Debug output `DEBUG`

Print the content of the `what` onto console and pass that unchanged.

Type: _Mapping_.

```
!DEBUG
what: !ITEM EVENT potatoes
```


### Include other declaration `INCLUDE`

Type: _Scalar_.

```
!INCLUDE declaration_identifier
```

Include the YAML declaration specified by `declaration_identifier` (which is dependant of the BSPump setup).
The content of the included YAML is placed in the position of the `!INCLUDE` expression.


### Get value from a configuration `CONFIG`

Type: _Scalar_.

```
!CONFIG configuration_key
```

Get the value from a configuration using `configuration_key`.
Configuration is a key/value space.

_Note_: Configuration items are resolved during YAML load time.



### Manipulate the context of the event processing `CONTEXT.SET`

Type: _Mapping_.

```
- !CONTEXT.SET
  what: <... expression ...>
  set:
    target: unparsed
```

This expression sets items into the `context` of the event (see `!CONTEXT`). The context contains various meta-data about the event processing.

`what` is optional, by default `None`. It will be directly passed to the output of this expression. It means that `!CONTEXT.SET` is no-op with a side effect on the event context.

Example of use in the parsing:

```
!FIRST
- !REGEX.PARSE
what: !EVENT
regex: '^(one)\s(two)\s(three)$'
items:
  - one
  - two
  - three
- !REGEX.PARSE
what: !EVENT
regex: '^(uno)\s(duo)\s(tres)$'
items:
  - one
  - two
  - three
# This is where the handling of partially parsed event starts
- !CONTEXT.SET
set:
  target: unparsed
- !DICT
set:
  unparsed: !EVENT
```

