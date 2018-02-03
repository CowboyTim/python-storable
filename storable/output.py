"""
import storable.output
storable.output.serialize({'x': 'bar', 'y': 1, 'z': 1.23, 'w':[], 'v':[1,2,3]})
"""
from struct import pack


def serialize(py_jsonable, pst_prefix=True, version=(5, 9)):
    ret_bytes = bytes()
    if pst_prefix:
        ret_bytes += b'pst0'
    ret_bytes += bytes(version)
    ret_bytes += process_item(py_jsonable)
    return ret_bytes


def unsigned_int(value, area=4):
    """
    Returns unsigned value with area param's byte-length
    This is also used for writing out the size
    """
    final = []
    for i in range(area-1, -1, -1):
        digit = 256**i
        dig_val = value // digit
        final.append(dig_val)
        value -= (dig_val * digit)
    return bytes(final)


def byte_len(size, area=4):
    return unsigned_int(size, area=area)


def signed_smallint(value):
    """
    Returns signed value
    """
    negative = (value < 0)
    value = abs(value)
    assert(value < 128)
    if not negative:
        value = value + 128
    return bytes([value])
signed_smallint.magic_type = b'\x08'


def signed_normalint(value, area=4):
    """
    Returns signed value
    """
    # TODO: accept cache arg and depend on int_unpack_fmt
    return pack('!i', value)
signed_normalint.magic_type = b'\x09'


def serialize_double(value):
    return pack('!d', value)
serialize_double.magic_type = b'\x07'


def serialize_scalar(scalar, area=1):
    if isinstance(scalar, bytes):
        ret_bytes = scalar
    else:
        ret_bytes = str(scalar).encode('utf-8')
    return bytes(byte_len(len(ret_bytes), area)
                 + ret_bytes)
serialize_scalar.magic_type = b'\x0a'


def serialize_longscalar(py_str):
    return serialize_scalar(py_str, area=4)
serialize_longscalar.magic_type = b'\x01'


def serialize_unicode(py_str):
    return serialize_scalar(py_str, area=4)
serialize_unicode.magic_type = b'\x18'


def serialize_null(isNone):
    return b''
serialize_null.magic_type = b'\x05'


def serialize_array(py_arr):
    # note, for 0-length arrays, it'll be the length
    # and then nothing after
    ret_bytes = bytes()
    return bytes(byte_len(len(py_arr))
                 + b''.join([process_item(x) for x in py_arr]))
serialize_array.magic_type = b'\x04\x02'  # reference, then array


def serialize_dict(py_dict):
    """
    dicts (or associative arrays) start with the
    *number of keys* (not byte length) and then
    does value-key pairs with the key mostly being
    a string
    """
    dict_len = len(py_dict)  # number of keys
    ret_bytes = bytes(byte_len(dict_len))
    for k, v in py_dict.items():
        ret_bytes += process_item(v)
        ret_bytes += serialize_longscalar(str(k))
    return ret_bytes
serialize_dict.magic_type = b'\x03'


INT_MAX = 2147483647


def detect_type(x):
    if isinstance(x, dict):
        return serialize_dict
    elif isinstance(x, list):
        return serialize_array
    elif isinstance(x, int):
        if -128 < x < 128:
            return signed_smallint
        elif abs(x) < INT_MAX:
            return signed_normalint
        else:
            # too big so print it out like a string
            return serialize_scalar
    elif isinstance(x, bool):
        return signed_smallint
    elif isinstance(x, float):
        if x > INT_MAX:
            return serialize_double
        else:
            return serialize_scalar
    elif x is None:
        return serialize_null
    elif isinstance(x, str):
        if max([ord(c) for c in x]) > 128:
            return serialize_unicode
        elif len(x) < 256:
            return serialize_scalar
        else:
            return serialize_longscalar
    else:
        raise NotImplementedError("unable to serialize %s" % x)


def process_item(x):
    method = detect_type(x)
    return bytes(method.magic_type
                 + method(x))
