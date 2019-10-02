from pymysql.converters import encoders as convertors
import numpy as np

""" Those methods extends pymysql convertor for numpy datatypes """


def convert_numpy_int(value, mapping=None):
    return str(value)


def convert_numpy_float(value, mapping=None):
    s = repr(value)
    if s in ('inf', 'nan'):
        raise ValueError("%s can not be used with MySQL" % s)
    if 'e' not in s:
        s += 'e0'
    return s


convertors[np.int8] = convert_numpy_int
convertors[np.int16] = convert_numpy_int
convertors[np.int32] = convert_numpy_int
convertors[np.int64] = convert_numpy_int

convertors[np.uint8] = convert_numpy_int
convertors[np.uint16] = convert_numpy_int
convertors[np.uint32] = convert_numpy_int
convertors[np.uint64] = convert_numpy_int

convertors[np.float16] = convert_numpy_float
convertors[np.float32] = convert_numpy_float
convertors[np.float64] = convert_numpy_float
