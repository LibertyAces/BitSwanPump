from pymysql.converters import encoders as convertors
import numpy as np

""" Those methods extends pymysql convertor for numpy datatypes """


def escape_numpy_int8(value, mapping=None):
    return str(value)


def escape_numpy_int16(value, mapping=None):
    return str(value)


def escape_numpy_int32(value, mapping=None):
    return str(value)


def escape_numpy_int64(value, mapping=None):
    return str(value)


def escape_numpy_uint8(value, mapping=None):
    return str(value)


def escape_numpy_uint16(value, mapping=None):
    return str(value)


def escape_numpy_uint32(value, mapping=None):
    return str(value)


def escape_numpy_uint64(value, mapping=None):
    return str(value)


def escape_numpy_float16(value, mapping=None):
    return str(value)


def escape_numpy_float32(value, mapping=None):
    return str(value)


def escape_numpy_float64(value, mapping=None):
    return str(value)


convertors[np.int8] = escape_numpy_int8
convertors[np.int16] = escape_numpy_int16
convertors[np.int32] = escape_numpy_int32
convertors[np.int64] = escape_numpy_int64

convertors[np.uint8] = escape_numpy_uint8
convertors[np.uint16] = escape_numpy_uint16
convertors[np.uint32] = escape_numpy_uint32
convertors[np.uint64] = escape_numpy_uint64

convertors[np.float16] = escape_numpy_float16
convertors[np.float32] = escape_numpy_float32
convertors[np.float64] = escape_numpy_float64



