
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

from struct import (calcsize, unpack)
import cStringIO as StringIO


def _read_size(fh, cache):
    fmt = cache['size_unpack_fmt']
    return unpack(fmt, fh.read(calcsize(fmt)))[0]


def SX_OBJECT(fh, cache):
    # From Storable.xs store function:
    # * The tag is always written in network order.
    i = SX_NETINT(fh, cache)
    cache['has_sx_object'] = True
    return (0, i)


def SX_LSCALAR(fh, cache):
    return fh.read(_read_size(fh, cache))


def SX_LUTF8STR(fh, cache):
    return SX_LSCALAR(fh, cache).decode('utf-8')


def SX_ARRAY(fh, cache):
    return [process_item(fh, cache) for i in xrange(_read_size(fh, cache))]


def SX_HASH(fh, cache):
    data = {}
    for i in xrange(_read_size(fh, cache)):
        value = process_item(fh, cache)
        key = fh.read(_read_size(fh, cache))
        data[key] = value
    return data


def SX_REF(fh, cache):
    return process_item(fh, cache)


def SX_UNDEF(fh, cache):
    return None


def SX_INTEGER(fh, cache):
    fmt = cache['int_unpack_fmt']
    return unpack(fmt, fh.read(calcsize(fmt)))[0]


def SX_DOUBLE(fh, cache):
    fmt = cache['double_unpack_fmt']
    return unpack(fmt, fh.read(calcsize(fmt)))[0]


def SX_BYTE(fh, cache):
    return _read_unsigned_byte(fh) - 128


def SX_NETINT(fh, cache):
    fmt = '!I'
    return unpack(fmt, fh.read(calcsize(fmt)))[0]


def SX_SCALAR(fh, cache):
    size = _read_unsigned_byte(fh)
    return fh.read(size)


def SX_UTF8STR(fh, cache):
    return SX_SCALAR(fh, cache).decode('utf-8')


def SX_TIED_ARRAY(fh, cache):
    return process_item(fh, cache)


def SX_TIED_HASH(fh, cache):
    return SX_TIED_ARRAY(fh, cache)


def SX_TIED_SCALAR(fh, cache):
    return SX_TIED_ARRAY(fh, cache)


def SX_SV_UNDEF(fh, cache):
    return None


def SX_SV_YES(fh, cache):
    return True


def SX_SV_NO(fh, cache):
    return False


def SX_BLESS(fh, cache):
    size = _read_unsigned_byte(fh)
    package_name = fh.read(size)
    cache['classes'].append(package_name)
    return process_item(fh, cache)


def SX_IX_BLESS(fh, cache):
    indx = _read_unsigned_byte(fh)
    package_name = cache['classes'][indx]
    return process_item(fh, cache)


def SX_OVERLOAD(fh, cache):
    return process_item(fh, cache)


def SX_TIED_KEY(fh, cache):
    data = process_item(fh, cache)
    key = process_item(fh, cache)
    return data


def SX_TIED_IDX(fh, cache):
    data = process_item(fh, cache)
    # idx's are always big-endian dumped by storable's freeze/nfreeze I think
    indx_in_array = SX_NETINT(fh, cache)
    return data


def SX_HOOK(fh, cache):
    flags = _read_unsigned_byte(fh)

    while flags & int(0x40):   # SHF_NEED_RECURSE
        dummy = process_item(fh, cache)
        flags = _read_unsigned_byte(fh)

    if flags & int(0x20):   # SHF_IDX_CLASSNAME
        if flags & int(0x04):   # SHF_LARGE_CLASSLEN
            # TODO: test
            fmt = '>I'
            indx = unpack(fmt, fh.read(calcsize(fmt)))[0]
        else:
            indx = _read_unsigned_byte(fh)
        package_name = cache['classes'][indx]
    else:
        if flags & int(0x04):   # SHF_LARGE_CLASSLEN
            # TODO: test
            # FIXME: is this actually possible?
            class_size = _read_size(fh, cache)
        else:
            class_size = _read_unsigned_byte(fh)

        package_name = fh.read(class_size)
        cache['classes'].append(package_name)

    arguments = {}

    if flags & int(0x08):   # SHF_LARGE_STRLEN
        str_size = _read_size(fh, cache)
    else:
        str_size = _read_unsigned_byte(fh)

    if str_size:
        frozen_str = fh.read(str_size)
        arguments[0] = frozen_str

    if flags & int(0x80):   # SHF_HAS_LIST
        if flags & int(0x10):   # SHF_LARGE_LISTLEN
            list_size = _read_size(fh, cache)
        else:
            list_size = _read_unsigned_byte(fh)

        for i in xrange(list_size):
            fmt = '>I'
            indx_in_array = unpack(fmt, fh.read(calcsize(fmt)))[0]
            arguments[i + 1] = cache['objects'].get(indx_in_array)

    # FIXME: implement the real callback STORABLE_thaw() still, for now, just
    # return the dictionary 'arguments' as data
    type = flags & int(0x03)  # SHF_TYPE_MASK 0x03
    data = arguments
    if type == 3:  # SHT_EXTRA
        # TODO
        #print("SHT_EXTRA")
        pass
    if type == 0:  # SHT_SCALAR
        # TODO
        #print("SHT_SCALAR")
        pass
    if type == 1:  # SHT_ARRAY
        # TODO
        #print("SHT_ARRAY")
        pass
    if type == 2:  # SHT_HASH
        # TODO
        #print("SHT_HASH")
        pass

    return data


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
    return tuple(int(x) for x in value[1:].split('.'))


def SX_LVSTRING(fh, cache):
    value = SX_LSCALAR(fh, cache)
    return tuple(int(x) for x in value[1:].split('.'))


# *AFTER* all the subroutines
engine = {
    '\x00': SX_OBJECT,      # ( 0): Already stored object
    '\x01': SX_LSCALAR,     # ( 1): Scalar (large binary) follows (length, data)
    '\x02': SX_ARRAY,       # ( 2): Array forthcoming (size, item list)
    '\x03': SX_HASH,        # ( 3): Hash forthcoming (size, key/value pair list)
    '\x04': SX_REF,         # ( 4): Reference to object forthcoming
    '\x05': SX_UNDEF,       # ( 5): Undefined scalar
    '\x06': SX_INTEGER,     # ( 6): Integer forthcoming
    '\x07': SX_DOUBLE,      # ( 7): Double forthcoming
    '\x08': SX_BYTE,        # ( 8): (signed) byte forthcoming
    '\x09': SX_NETINT,      # ( 9): Integer in network order forthcoming
    '\x0a': SX_SCALAR,      # (10): Scalar (binary, small) follows (length, data)
    '\x0b': SX_TIED_ARRAY,  # (11): Tied array forthcoming
    '\x0c': SX_TIED_HASH,   # (12): Tied hash forthcoming
    '\x0d': SX_TIED_SCALAR, # (13): Tied scalar forthcoming
    '\x0e': SX_SV_UNDEF,    # (14): Perl's immortal PL_sv_undef
    '\x0f': SX_SV_YES,      # (15): Perl's immortal PL_sv_yes
    '\x10': SX_SV_NO,       # (16): Perl's immortal PL_sv_no
    '\x11': SX_BLESS,       # (17): Object is blessed
    '\x12': SX_IX_BLESS,    # (18): Object is blessed, classname given by index
    '\x13': SX_HOOK,        # (19): Stored via hook, user-defined
    '\x14': SX_OVERLOAD,    # (20): Overloaded reference
    '\x15': SX_TIED_KEY,    # (21): Tied magic key forthcoming
    '\x16': SX_TIED_IDX,    # (22): Tied magic index forthcoming
    '\x17': SX_UTF8STR,     # (23): UTF-8 string forthcoming (small)
    '\x18': SX_LUTF8STR,    # (24): UTF-8 string forthcoming (large)
    '\x19': SX_FLAG_HASH,   # (25): Hash with flags forthcoming (size, flags, key/flags/value triplet list)
    '\x1d': SX_VSTRING,     # (29): vstring forthcoming (small)
    '\x1e': SX_LVSTRING,    # (30): vstring forthcoming (large)
}


exclude_for_cache = {'\x00', '\x0b', '\x0c', '\x0d', '\x11', '\x12'}


def handle_sx_object_refs(cache, data):
    iterateelements = None
    if type(data) is list:
        iterateelements = enumerate(data)
    elif type(data) is dict:
        iterateelements = data.iteritems()
    else:
        return

    for k, item in iterateelements:
        if type(item) is list or type(item) is dict:
            handle_sx_object_refs(cache, item)
        elif type(item) is tuple:
            data[k] = cache['objects'][item[1]]
    return data


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


def thaw(frozen_data):
    fh = StringIO.StringIO(frozen_data)
    return deserialize(fh)


def retrieve(file):
    with open(file, 'rb') as fh:
        file_magic = fh.read(4)
        if file_magic == 'pst0':
            return deserialize(fh)


def _read_unsigned_byte(fh):
    return unpack('B', fh.read(1))[0]


def deserialize(fh):
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

        if archsize == '1234' or archsize == '12345678':
            byteorder = '<'
        else:
            byteorder = '>'

        intsize, longsize, ptrsize = unpack('3B', fh.read(3))
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
