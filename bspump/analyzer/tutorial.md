# Analyzers and Matrices exhaustive tutorial

## General

`Analyzer` is a special type of processor in `bspump`, that passes events unchanged, but aggregates the information about them
in some object. There are analyzers operating on `Matrix`, the top-level object of `bspump`. So far there are 3 types of matrices,
`SessionMatrix`, `TimeWindowMatrix` and `GeoMatrix`. The analyzers on these matrices are `SessionAnalyzer`, `TimeWindowAnalyzer`
and `GeoAnalyzer` respectively.

## Initialization

The `Matrix` can be initialized outside of the `Analyzer` and passed as `matrix_id` into the `Analyzer` (next chapter), as many analyzers can
operate on the same matrix.
The other way is to pass all matrix's parameters to the analyzer's constructor (will be discussed later).

## SessionMatrix

### Initialization

Parameters in the constructor: `app`, `dtype='float_'`, `id=None`, `config=None`. I guess you're familiar with all of them except for `dtype`. 
`SessionMatrix` has columns with different names and types. For instance, you want to keep in the matrix 3 columns: `timestamp` as integer,
`tag` as string and `some_numbers` as float submatrix with 2 rows and 2 columns. That brings `dtype`, which has to be a list in the form `dtype=[('timestamp', 'i8'), ('tag', 'U20'), ('some_numbers','(2,2)f8')]`. The first tuple member is a name, the second is a type. `i8` means 8 bit integer, `U20` means unicode string length at most 20 characters and `(2,2)f8` means 8 bit float matrix with size (2, 2).

### Attributes
`Array` is the `numpy` matrix. Consists of rows and columns and cells.
`N2IMap` structure helping to translate row name (unique id) to numeric array index/
`I2NMap` index-to-row-name translation.
`ClosedRows` is a set, containing temporaly unused row indeces. 

### Functions

`row_index = SessionMatrix.add_row(row_name)` adds new row with specific id and returns numerical index of the row in the matrix.
`row_index = SessionMatrix.get_row_index(row_name)` translates `row_id` to the index in matrix, `None` if does not exist. 
`row_name = SessionMatrix.get_row_name(row_index)` translates `row_name` to the name or id, `None` if does not exist.
`SessionMatrix.close_row(row_index)` adds index to `ClosedRows`.
`SessionMatrix.flush()` deletes closed rows from the matrix.

## TimeWindowMatrix

### Initialization

Parameters in the constructor (with defaults) `app`, `dtype='float_'`, `resolution=60`, `columns=15`,  `clock_driven=True`, `start_time=None`, `id=None`, `config=None`. 
`TimeWindowMatrix` has a time dimension columns, where events with timestamp are aggregated. You may notice, that `dtype` is not a list unlike `SessionMatrix`,fist number represent number of columns (first member of tuple) and number of cells inside each column (second member). `resolution` means number of seconds in each time column of the Matrix. `clock_driven=True` means, that time window once in a while will be moving forward by adding 
newest column and deleting the oldest one. The period of advancing is `resolution`. `start_time` is a timestamp of starting, if it's `None`, the start time will be current time.

### Attributes

(same as `SessionMatrix`)
additional ones:
`Start` newest timestamp is seconds.
`End` oldest timestamp is seconds.
`Resolution` seconds in each column.
`Dimensions` (number of columns, cells in column)
`WarmingUpCount` array indicating if added row is 'old' enough to be analyzed.

### Functions
(same as `SessionMatrix`)
plus:
`column_index = TimeWindowMatrix.get_column(timestamp)` returns column index of the cell the timestamp (in seconds) belongs to.
`None`, if it's outside.
`TimeWindowMatrix.advance(target_timestamp)` possibly move forward the time window


## GeoMatrix

### Initialization

Parameters in the constructor (with defaults) `app`, `dtype='float_'`, `bbox=None`, `resolution=5`, `id=None`, `config=None`.
`GeoMatrix` is fixed size matrix, representing the map. Real GPS coordinates are projected to map coordinates using equirectangular 
transformation. `dtype` see `SessionMatrix` section. `bbox` is a dictionary with map extreme points
`max_lat`, `min_lat`, `min_lon`, `max_lon`. If `None`, it takes european coordinates.
`resolution` is the size of the cell in kilometers. 

### Attributes
`Array` is the `numpy` matrix. Consists of rows and columns and cells.
`BBox` is a bounding box (see initialization section).
`Resolution` is the size of the cell in kilometers.
`MembersToIds`
`SizeWidth` width of map in km
`SizeHeight` height of map in km
`MapWidth`  number of rows in matrix (alias of `Array.shape[0]`)
`MapHeight` number of columns in matrix (alias of `Array.shape[1]`)

### Functions
`is_in_boundaries(lat, lon)` tests if coordinates fall into the map, returns boolean.
`row, column = project_equirectangular(lat, lon)` translates real coordinates to map coordinates, using equirectangular transformation.
`lat, lon = inverse_equirectangular(row, column)` translates map coordinates into gps coordinates.

## Analyzers initialization

### SessionAnalyzer

Parameters of the constructor `app`, `pipeline`, `dtype='float_'`, `matrix_id=None`, `analyze_on_clock=False`, `id=None`, `config=None`.
`dtype` is passed to `Matrix` if needed. If `matrix_id` is present, the pre-created matrix will be 'located'.
`analyze_on_clock` enables the call of `analyze()` function by timer. There should be added `'analyze_period':time_in_seconds` to `config`.
Default period is 1 minute.

### TimeWindowAnalyzer
Parameters of the constructor `app`, `pipeline`, `matrix_id=None`, `dtype='float_'`, `columns=15`, `analyze_on_clock=False`, `resolution=60`, 
`start_time=None`, `clock_driven=True`, `id=None`, `config=None`. If `matrix_id` is present, the pre-created matrix will be 'located'.
`analyze_on_clock` enables the call of `analyze()` function by timer. There should be added `'analyze_period':time_in_seconds` to `config`.
Default period is 1 minute.

### GeoAnalyzer
Parameters in constructor `app`, `pipeline`, `dtype='float'`, `matrix_id=None`, `analyze_on_clock=False`, `bbox=None`, `resolution=5`, `id=None`, `config=None`
(see `GeoMatrix` and `SessioAnalyzer`).

## The lifecycle of an Analyzer
Any `Analyzer` is a processor, it means, it has `process()` function. By default it is:
```
def process(self, context, event):
	if self.predicate(context, event):
		self.evaluate(context, event)
	return event
```

`predicate()` should filter incoming events and return `boolean`. By default always returns `True`.
`evaluate()` is main function, where the information should be aggregated.
Example:
```
def evaluate(self, context, event):
	row_index = self.TimeWindow.get_row_index(event['some_id'])
	if row_index is None:
		row_index = self.TimeWindow.add_row(event['some_id'])

	column_index = self.TimeWindow.get_column(event['@timestamp']) # not need if SessionMatrix
	if column_index is None:
		# do nothing
		return

	self.TimeWindow.Array[row_index, column_index, SOME_DIMENSION_YOU_NEED] = event['some_attribute']
	# self.Sessions.Array['some_column'][row_index] = event['some_attribute']
	...
```
Each `Analyzer` has an `analyze()` function, which can be called internally or externally, depends on your needs.
Typically `analyze()` produces events based on the object of analyzis (usually `Matrix`) to some external source.
It is specific for each analyzer.
If the analyzed object is `Matrix`, it is not recommended to iterate through the matrix row by row (or cell by cell).
Instead use numpy fuctions. Examples:
1. You have a vector with n rows. You need only those row indeces, where the cell content is more than 10.
Use `np.where(vector > 10)`.
2. You have a matrix with n rows and m columns. You need to find out which rows
fully consist of zeros. use `np.where(np.all(matrix == 0, axis=1))` to get those row indexes.
Instead `np.all()` you can use `np.any()` to get all row indexes, where there is at least one zero.  
3. Use `np.mean(matrix, axis=1)` to get means for all rows.
4. Usefull numpy functions: `np.unique()`, `np.sum()`, `np.argmin()`, `np.argmax()`. 

## Other analyzers

There exist other kinds of `Analyzer` not using the `Matrix` object. 
They are `LatchAnalyzer` which stores last n events. `TimeDriftAnalyzer` creates a 
metric of statistic about events' timestamps with current time difference.


