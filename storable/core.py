#
# License
#
# python storable is distributed under the zlib/libpng license, which is OSS
# (Open Source Software) compliant.
#
# Copyright (C) 2009 Tim Aerts
#
# This software is provided 'as-is', without any express or implied
# warranty.  In no event will the authors be held liable for any damages
# arising from the use of this software.
#
# Permission is granted to anyone to use this software for any purpose,
# including commercial applications, and to alter it and redistribute it
# freely, subject to the following restrictions:
#
# 1. The origin of this software must not be misrepresented; you must not
#    claim that you wrote the original software. If you use this software
#    in a product, an acknowledgment in the product documentation would be
#    appreciated but is not required.
# 2. Altered source versions must be plainly marked as such, and must not be
#    misrepresented as being the original software.
# 3. This notice may not be removed or altered from any source distribution.
#
# Tim Aerts <aardbeiplantje@gmail.com>
#

from __future__ import unicode_literals
from past.builtins import basestring
from functools import wraps
import io
from struct import calcsize, unpack
import logging
import os
import sys


if sys.version_info > (3, 0):
    xrange = range


def id_():
    n = 0
    while True:
        n += 1
        yield n


# logging setup
ID_GENERATOR = id_()
loglevel = os.getenv('PYTHON_STORABLE_LOGLEVEL', 'INFO').upper()
logging.basicConfig(level=loglevel,format=f'[%(levelname)s] %(asctime)s [{os.getpid()}] %(message)s',datefmt="%Y-%m-%dT%H:%M:%S.000Z")
logger = logging.getLogger()
logger.setLevel(loglevel)
DEBUG = False
if loglevel == 'DEBUG':
    DEBUG = True


def _guess_type(data):
    """
    In Perl, the "scalar" type maps to different Python types. Strictly
    speaking, the only *correct* output would be bytes objects. But this causes
    a discrepancy when using "frozen" storables and non-frozen storables (unless
    the generated test-data is wrong). For now, we will use the conversion
    functions below to "guess" the type.
    """
    try:
        converted_result = float(data)
        if converted_result.is_integer():
            # use "data" again to avoid rounding errors
            converted_result = int(data)
    except ValueError:
        converted_result = None

    if converted_result is None:
        try:
            converted_result = data.decode('ascii')
        except UnicodeDecodeError:
            converted_result = None

    return data if converted_result is None else converted_result


def maybelogged(f):
    """
    If the DEBUG flag is set in this module (must be set before importing),
    deserialisation functions will be logged.
    """
    if not DEBUG:
        return f

    @wraps(f)
    def fun(*args, **kwargs):

        id_ = next(ID_GENERATOR)
        logger.debug('[%s] Entering %s with args=%r, kwargs=%r',
                  id_, f.__name__, args, kwargs)
        output = f(*args, **kwargs)
        logger.debug('[%s] Result: %r', id_, output)
        return output
    return fun


@maybelogged
def _read_size(fh, cache):
    fmt = cache['size_unpack_fmt']
    return unpack(fmt, fh.read(calcsize(fmt)))[0]


@maybelogged
def SX_OBJECT(fh, cache):
    # From Storable.xs store function:
    # * The tag is always written in network order.
    i = SX_NETINT(fh, cache)
    cache['has_sx_object'] = True
    return (0, i)


@maybelogged
def SX_LSCALAR(fh, cache):
    raw_result = fh.read(_read_size(fh, cache))
    return _guess_type(raw_result)


@maybelogged
def SX_LUTF8STR(fh, cache):
    return fh.read(_read_size(fh, cache)).decode('utf-8')


@maybelogged
def SX_ARRAY(fh, cache):
    return [process_item(fh, cache) for _ in xrange(_read_size(fh, cache))]


@maybelogged
def SX_HASH(fh, cache):
    data = {}
    sz = _read_size(fh, cache)
    for _ in xrange(sz):
        value = process_item(fh, cache)
        key = _guess_type(fh.read(_read_size(fh, cache)))
        data[key] = value
    return data


@maybelogged
def SX_REF(fh, cache):
    return process_item(fh, cache)


@maybelogged
def SX_UNDEF(fh, cache):
    return None


@maybelogged
def SX_INTEGER(fh, cache):
    fmt = cache['int_unpack_fmt']
    return unpack(fmt, fh.read(calcsize(fmt)))[0]


@maybelogged
def SX_DOUBLE(fh, cache):
    fmt = cache['double_unpack_fmt']
    return unpack(fmt, fh.read(calcsize(fmt)))[0]


@maybelogged
def SX_BYTE(fh, cache):
    return _read_unsigned_byte(fh) - 128


@maybelogged
def SX_NETINT(fh, cache):
    fmt = '!I'
    return unpack(fmt, fh.read(calcsize(fmt)))[0]


@maybelogged
def SX_SCALAR(fh, cache):
    size = _read_unsigned_byte(fh)
    raw_result = fh.read(size)
    return _guess_type(raw_result)


@maybelogged
def SX_UTF8STR(fh, cache):
    return fh.read(_read_unsigned_byte(fh)).decode('utf-8')


@maybelogged
def SX_TIED_ARRAY(fh, cache):
    return process_item(fh, cache)


@maybelogged
def SX_TIED_HASH(fh, cache):
    return SX_TIED_ARRAY(fh, cache)


@maybelogged
def SX_TIED_SCALAR(fh, cache):
    return SX_TIED_ARRAY(fh, cache)


@maybelogged
def SX_SV_UNDEF(fh, cache):
    return None


@maybelogged
def SX_SV_YES(fh, cache):
    return True


@maybelogged
def SX_SV_NO(fh, cache):
    return False


@maybelogged
def SX_BLESS(fh, cache):
    size = _read_unsigned_byte(fh)
    package_name = fh.read(size)
    cache['classes'].append(package_name)
    return process_item(fh, cache)


@maybelogged
def SX_IX_BLESS(fh, cache):
    indx = _read_unsigned_byte(fh)
    package_name = cache['classes'][indx]
    return process_item(fh, cache)


@maybelogged
def SX_OVERLOAD(fh, cache):
    return process_item(fh, cache)


@maybelogged
def SX_TIED_KEY(fh, cache):
    data = process_item(fh, cache)
    key = process_item(fh, cache)
    return data


@maybelogged
def SX_TIED_IDX(fh, cache):
    data = process_item(fh, cache)
    # idx's are always big-endian dumped by storable's freeze/nfreeze I think
    indx_in_array = SX_NETINT(fh, cache)
    return data


@maybelogged
def SX_HOOK(fh, cache):
    flags = _read_unsigned_byte(fh)

    while flags & 0x40:   # SHF_NEED_RECURSE
        dummy = process_item(fh, cache)
        flags = _read_unsigned_byte(fh)

    if flags & 0x20:   # SHF_IDX_CLASSNAME
        if flags & 0x04:   # SHF_LARGE_CLASSLEN
            # TODO: test
            fmt = '>I'
            indx = unpack(fmt, fh.read(calcsize(fmt)))[0]
        else:
            indx = _read_unsigned_byte(fh)
        package_name = cache['classes'][indx]
    else:
        if flags & 0x04:   # SHF_LARGE_CLASSLEN
            # TODO: test
            # FIXME: is this actually possible?
            class_size = _read_size(fh, cache)
        else:
            class_size = _read_unsigned_byte(fh)

        package_name = fh.read(class_size)
        cache['classes'].append(package_name)

    arguments = {}

    if flags & 0x08:   # SHF_LARGE_STRLEN
        str_size = _read_size(fh, cache)
    else:
        str_size = _read_unsigned_byte(fh)

    if str_size:
        frozen_str = _guess_type(fh.read(str_size))
        arguments[0] = frozen_str

    if flags & 0x80:   # SHF_HAS_LIST
        if flags & 0x10:   # SHF_LARGE_LISTLEN
            list_size = _read_size(fh, cache)
        else:
            list_size = _read_unsigned_byte(fh)

        for i in xrange(list_size):
            fmt = '>I'
            indx_in_array = unpack(fmt, fh.read(calcsize(fmt)))[0]
            arguments[i + 1] = cache['objects'].get(indx_in_array)

    # FIXME: implement the real callback STORABLE_thaw() still, for now, just
    # return the dictionary 'arguments' as data
    type = flags & 0x03  # SHF_TYPE_MASK 0x03
    data = arguments
    if type == 3:  # SHT_EXTRA
        # TODO
        pass
    if type == 0:  # SHT_SCALAR
        # TODO
        pass
    if type == 1:  # SHT_ARRAY
        # TODO
        pass
    if type == 2:  # SHT_HASH
        # TODO
        pass

    return data


@maybelogged
def SX_FLAG_HASH(fh, cache):
    # TODO: NOT YET IMPLEMENTED!!!!!!
    flags = _read_unsigned_byte(fh)
    size = _read_size(fh, cache)
    data = {}
    for i in xrange(size):
        value = process_item(fh, cache)
        flags = _read_unsigned_byte(fh)
        keysize = _read_size(fh, cache)
        key = None
        if keysize:
            key = fh.read(keysize)
        data[key] = value

    return data


def SX_VSTRING(fh, cache):
    value = SX_SCALAR(fh, cache)
    return tuple(x for x in value[1:].split('.'))


def SX_LVSTRING(fh, cache):
    value = SX_LSCALAR(fh, cache)
    return tuple(x for x in value[1:].split('.'))


# *AFTER* all the subroutines
engine = {
    b'\x00': SX_OBJECT,      # ( 0): Already stored object
    b'\x01': SX_LSCALAR,     # ( 1): Scalar (large binary) follows (length, data)
    b'\x02': SX_ARRAY,       # ( 2): Array forthcoming (size, item list)
    b'\x03': SX_HASH,        # ( 3): Hash forthcoming (size, key/value pair list)
    b'\x04': SX_REF,         # ( 4): Reference to object forthcoming
    b'\x05': SX_UNDEF,       # ( 5): Undefined scalar
    b'\x06': SX_INTEGER,     # ( 6): Integer forthcoming
    b'\x07': SX_DOUBLE,      # ( 7): Double forthcoming
    b'\x08': SX_BYTE,        # ( 8): (signed) byte forthcoming
    b'\x09': SX_NETINT,      # ( 9): Integer in network order forthcoming
    b'\x0a': SX_SCALAR,      # (10): Scalar (binary, small) follows (length, data)
    b'\x0b': SX_TIED_ARRAY,  # (11): Tied array forthcoming
    b'\x0c': SX_TIED_HASH,   # (12): Tied hash forthcoming
    b'\x0d': SX_TIED_SCALAR, # (13): Tied scalar forthcoming
    b'\x0e': SX_SV_UNDEF,    # (14): Perl's immortal PL_sv_undef
    b'\x0f': SX_SV_YES,      # (15): Perl's immortal PL_sv_yes
    b'\x10': SX_SV_NO,       # (16): Perl's immortal PL_sv_no
    b'\x11': SX_BLESS,       # (17): Object is blessed
    b'\x12': SX_IX_BLESS,    # (18): Object is blessed, classname given by index
    b'\x13': SX_HOOK,        # (19): Stored via hook, user-defined
    b'\x14': SX_OVERLOAD,    # (20): Overloaded reference
    b'\x15': SX_TIED_KEY,    # (21): Tied magic key forthcoming
    b'\x16': SX_TIED_IDX,    # (22): Tied magic index forthcoming
    b'\x17': SX_UTF8STR,     # (23): UTF-8 string forthcoming (small)
    b'\x18': SX_LUTF8STR,    # (24): UTF-8 string forthcoming (large)
    b'\x19': SX_FLAG_HASH,   # (25): Hash with flags forthcoming (size, flags, key/flags/value triplet list)
    b'\x1d': SX_VSTRING,     # (29): vstring forthcoming (small)
    b'\x1e': SX_LVSTRING,    # (30): vstring forthcoming (large)
}


exclude_for_cache = {
    b'\x00',
    b'\x0b',
    b'\x0c',
    b'\x0d',
    b'\x11',
    b'\x12',
}


@maybelogged
def handle_sx_object_refs(cache, data):
    iterateelements = None
    if type(data) is list:
        iterateelements = enumerate(data)
    elif type(data) is dict:
        iterateelements = iter(data.items())
    else:
        return

    for k, item in iterateelements:
        if type(item) is list or type(item) is dict:
            handle_sx_object_refs(cache, item)
        elif type(item) is tuple:
            data[k] = cache['objects'][item[1]]
    return data


@maybelogged
def process_item(fh, cache):
    magic_type = fh.read(1)
    if magic_type in exclude_for_cache:
        data = engine[magic_type](fh, cache)
    else:
        i = cache['objectnr']
        cache['objectnr'] += 1
        data = engine[magic_type](fh, cache)
        cache['objects'][i] = data
    return data


@maybelogged
def thaw(frozen_data):
    fh = io.BytesIO(frozen_data)
    data = deserialize(fh)
    fh.close()
    return data


@maybelogged
def retrieve(filepath):
    data = None
    with open(filepath, 'rb') as fh:
        file_magic = fh.read(4)
        if file_magic == b'pst0':
            data = deserialize(fh)
    return data


def _read_unsigned_byte(fh):
    return unpack('B', fh.read(1))[0]


def skip_magic_header_if_present(fh):
    curr_pos = fh.tell()
    file_magic = fh.read(4)
    if file_magic != b'pst0':
        fh.seek(curr_pos)


@maybelogged
def deserialize(fh):
    skip_magic_header_if_present(fh)
    magic_byte = _read_unsigned_byte(fh)

    is_network_byte_order = (magic_byte & 1) == 1
    major_version_number = magic_byte >> 1
    minor_version_number = _read_unsigned_byte(fh)

    nvsize = 8  # Size of double in bytes
    integer_formats = {
        2: 'H',
        4: 'I',
        8: 'Q',
    }
    double_formats = {
        4: 'f',
        8: 'd',
    }
    if is_network_byte_order:
        byteorder = '!'
        # TODO: unsure what these values should be when reading a net-order
        # file
        intsize = 4
        longsize = 8
        ptrsize = 4
    else:
        size = _read_unsigned_byte(fh)
        archsize = fh.read(size)

        # 32-bit ppc:     4321
        # 32-bit x86:     1234
        # 64-bit x86_64:  12345678
        # 64-bit ppc:     87654321

        if archsize == b'1234' or archsize == b'12345678':
            byteorder = '<'
        else:
            byteorder = '>'

        x = fh.read(3)
        intsize, longsize, ptrsize = unpack('3B', x)
        if (major_version_number, minor_version_number) >= (2, 2):
            nvsize = _read_unsigned_byte(fh)
            if nvsize > 8:
                raise ValueError('Cannot handle 16 byte doubles')

    cache = {
        'objects': {},
        'objectnr': 0,
        'classes': [],
        'has_sx_object': False,
        'size_unpack_fmt': byteorder + integer_formats[intsize],
        'int_unpack_fmt': byteorder + integer_formats[longsize],
        'double_unpack_fmt': byteorder + double_formats[nvsize],
    }
    data = process_item(fh, cache)

    if cache['has_sx_object']:
        handle_sx_object_refs(cache, data)

    return data


@maybelogged
def freeze(py_jsonable, pst_prefix=True, version=(5, 9)):
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
        serialized_value = serialize_method(value)
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


@maybelogged
def unsigned_int(value, area=4, depth=0):
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


@maybelogged
def byte_len(size, area=4):
    return unsigned_int(size, area=area)


@maybelogged
def signed_smallint(value, depth=0):
    """
    Returns signed value
    """
    negative = (value < 0)
    value = abs(value)
    if value >= 128:
        raise ValueError("A small int must be less <128 to fit in a byte.")
    if not negative:
        value = value + 128
    return b'\x08' + bytes(bytearray([value]))


@maybelogged
def signed_normalint(value, area=4, depth=0):
    """
    Returns signed value
    """
    # TODO: accept cache arg and depend on int_unpack_fmt
    return b'\x09' + pack('!i', value)


@maybelogged
def serialize_double(value, depth=0):
    return b'\x07' + pack('!d', value)


@maybelogged
def serialize_string(s, area=4, depth=0):
    if isinstance(s, bytes):
        ret_bytes = s
    elif isinstance(s, basestring):
        ret_bytes = s.encode('utf-8')
    elif isinstance(s, io.BytesIO):
        ret_bytes = s.read().encode('utf-8')
    elif isinstance(s, io.BufferedReader):
        ret_bytes = s.read().encode('utf-8')
    else:
        ret_bytes = str(s).encode('utf-8')
    return bytes(byte_len(len(ret_bytes), area) + ret_bytes)

@maybelogged
def serialize_scalar(py_str, depth=0):
    return b'\x0a' + serialize_string(py_str, area=1, depth=depth)

@maybelogged
def serialize_longscalar(py_str, depth=0):
    return b'\x01' + serialize_string(py_str, area=4, depth=depth)


@maybelogged
def serialize_unicode(py_str, depth=0):
    return b'\x18' + serialize_string(py_str, area=4, depth=depth)


@maybelogged
def serialize_null(isNone, depth=0):
    return b'\x05' + b''


@maybelogged
def serialize_array(py_arr, depth=0):
    # note, for 0-length arrays, it'll be the length
    # and then nothing after
    prefix = b''
    if depth == 0:
        prefix = b'\x02'
    else:
        prefix = b'\x04\x02'
    return prefix + bytes(byte_len(len(py_arr)) + b''.join([process_item(x, depth=depth+1) for x in py_arr]))


@maybelogged
def serialize_dict(py_dict, depth=0):
    """
    dicts (or associative arrays) start with the
    *number of keys* (not byte length) and then
    does value-key pairs with the key mostly being
    a string
    """
    dict_len = len(py_dict)  # number of keys
    v_bytes = b''
    for k, v in py_dict.items():
        v_bytes += process_item(v, depth=depth+1)
        v_bytes += serialize_string(str(k), depth=depth)
    prefix = b''
    if depth == 0:
        prefix = b'\x03'
    else:
        prefix = b'\x04\x03'
    return prefix + bytes(byte_len(dict_len)) + v_bytes


INT_MAX = 2147483647


@maybelogged
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
    elif isinstance(x, io.BytesIO):
        return serialize_longscalar
    elif isinstance(x, io.BufferedReader):
        return serialize_longscalar
    elif isinstance(x, basestring):
        if max([ord(c) for c in x]) > 128:
            return serialize_unicode
        elif len(x) < 256:
            return serialize_scalar
        else:
            return serialize_longscalar
    else:
        raise NotImplementedError("unable to serialize type %s with value %s" % (type(x), x))


@maybelogged
def process_item(x, depth=0):
    method = detect_type(x)
    return bytes(method(x, depth=depth))


