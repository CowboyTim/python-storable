from __future__ import unicode_literals

"""
import storable.output
storable.output.serialize({'x': 'bar', 'y': 1, 'z': 1.23, 'w':[], 'v':[1,2,3]})
"""
from struct import pack
from storable.core import thaw

try:
    basestring  # python2.7 compatibility
except NameError:
    basestring = str


def serialize(py_jsonable, pst_prefix=True, version=(5, 9)):
    ret_bytes = bytes()
    if pst_prefix:
        ret_bytes += b'pst0'
    ret_bytes += bytes(bytearray(version))
    ret_bytes += process_item(py_jsonable)
    return ret_bytes


def modify_hash(serialized, key, value, serialize_method=None):
    """
    For a limited set of storables which must:
    * be in network byte order
    * be a hash/dict at the base-level
    you can use this method to add/modify keys as long as the
    new value serializes similarly.  This allows you to keep
    ref/object information from the original while only updating
    a specific 'simple' value (e.g. integer, etc.

    When running this method, make sure you wrap in a
    try...except ValueError... as any violation of the
    necessary parameters will raise one.
    """
    if not isinstance(key, basestring):
        raise ValueError("Keys must be strings")
    size_start = 3
    if serialized.startswith(b'pst0'):
        size_start += 4
    magic_byte = serialized[size_start - 3]
    magic_byte = magic_byte if isinstance(magic_byte, int) else ord(magic_byte)
    is_network_byte_order = (magic_byte & 1) == 1
    if not is_network_byte_order:
        raise ValueError("serialized object must be in network byte order"
                         ", not machine-specific")
    full = thaw(serialized)
    serialized_value = None
    if serialize_method:
        serialized_value = (serialize_method.magic_type
                            + serialize_method(value))
    else:
        serialized_value = process_item(value)
    serialized_key = serialize_longscalar(str(key))
    if key in full:
        # Just going to modify in-place
        # We need a unique key in the serialization or we can't (as easily)
        # figure out where to update:
        if serialized.count(serialized_key) != 1:
            raise ValueError("Key occurred more than once, "
                             "so intrusive modification is impossible")
        # Make sure it's not a variable-length value
        # or if it is, that the replacement is the same length
        if not (serialize_method  # trust caller
                or not hasattr(value, '__len__')
                or len(value) == len(full[key])):
            raise ValueError(
                "Value parameter is not same-length as the existing value"
            )
        key_start = serialized.index(serialized_key)
        value_start = key_start - len(serialized_value)
        # make sure the type-byte aligns.
        if serialized_value[0] != serialized[value_start]:
            raise ValueError(
                "Value parameter did not match the existing parameter type. "
                "Try adding a serialize_method argument, "
                "to force the right type.")
        return (serialized[:value_start]
                + serialized_value
                + serialized[key_start:])
    else:
        # Need to update key-count and append
        return (serialized[:size_start]
                + unsigned_int(len(full) + 1)  # updated length
                + serialized[size_start + 4:]
                + serialized_value
                + serialized_key)


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
    return bytes(bytearray(final))


def byte_len(size, area=4):
    return unsigned_int(size, area=area)


def signed_smallint(value):
    """
    Returns signed value
    """
    negative = (value < 0)
    value = abs(value)
    if value >= 128:
        raise ValueError("A small int must be less <128 to fit in a byte.")
    if not negative:
        value = value + 128
    return bytes(bytearray([value]))
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
    elif isinstance(scalar, basestring):
        ret_bytes = scalar.encode('utf-8')
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
    elif isinstance(x, basestring):
        if max([ord(c) for c in x]) > 128:
            return serialize_unicode
        elif len(x) < 256:
            return serialize_scalar
        else:
            return serialize_longscalar
    else:
        raise NotImplementedError(
            "unable to serialize type %s with value %s" % (type(x), x)
        )


def process_item(x):
    method = detect_type(x)
    return bytes(method.magic_type
                 + method(x))
