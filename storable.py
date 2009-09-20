
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

from struct import unpack

def thaw(fh):
    magic = fh.read(2)
    if magic == '\x05\x07':
        print("OK:nfreeze") 
    if magic == '\x04\x07':
        magic = fh.read(9)
        if magic == '\x04\x34\x33\x32\x31\x04\x04\x04\x08':
            print("OK:freeze") 

    cache = { 'objects' : [], 'classes' : [] } 
    return process_item(fh, cache)

def process_item(fh, cache):
    data = None
    magic_type = fh.read(1)
    if   magic_type == '\x00':  # SX_OBJECT      ( 0): Already stored object
        i = unpack('i', fh.read(4))[0]
        print("stored object, nr:"+str(i))
        data = cache['objects'][i-1]
    elif magic_type == '\x01' \
      or magic_type == '\x18':
                                # SX_LSCALAR     ( 1): Scalar (large binary) follows (length, data)
                                # SX_LUTF8STR    (24): UTF-8 string forthcoming (large)
        size = unpack('i', fh.read(4))[0]
        print("big scalar, size:"+str(size))
        data = fh.read(size)
    elif magic_type == '\x02':  # SX_ARRAY       ( 2): Array forthcoming (size, item list)
        size = unpack('i', fh.read(4))[0]
        print("array, size:"+str(size))
        data = [process_item(fh, cache) for i in range(0,size)]
    elif magic_type == '\x03':  # SX_HASH        ( 3): Hash forthcoming (size, key/value pair list)
        size = unpack('i', fh.read(4))[0]
        print("array, size:"+str(size))
        data = {}
        for i in range(0,size):
            value = process_item(fh, cache)
            size  = unpack('i', fh.read(4))[0]
            key   = fh.read(size)
            data[key] = value
    elif magic_type == '\x04':  # SX_REF         ( 4): Reference to object forthcoming
        print("ref to next")
        # in fact: ignored, python doesn't have/need them, although a GOTO
        # would consume less memory/cpu by not executing another method ;-)
        data = process_item(fh, cache)
    elif magic_type == '\x05':  # SX_UNDEF       ( 5): Undefined scalar
        print("scalar undef")
        data = None
    elif magic_type == '\x07':  # SX_DOUBLE      ( 7): Double forthcoming
        print("double")
        data = unpack('d', fh.read(8))[0]
    elif magic_type == '\x08':  # SX_BYTE        ( 8): (signed) byte forthcoming
        print("scalar byte")
        data = unpack('B', fh.read(1))[0] - 128
    elif magic_type == '\x0a' \
      or magic_type == '\x17':
                                # SX_SCALAR      (10): Scalar (binary, small) follows (length, data)
                                # SX_UTF8STR     (23): UTF-8 string forthcoming (small)
        size = unpack('B', fh.read(1))[0]
        print("small scalar, size:"+str(size))
        data = fh.read(size)
    elif magic_type == '\x0b' \
      or magic_type == '\x0c' \
      or magic_type == '\x0d':
                                # SX_TIED_ARRAY  (11): Tied array forthcoming
                                # SX_TIED_HASH   (12): Tied hash forthcoming
                                # SX_TIED_SCALAR (13): scalar hash forthcoming
        print("tied")
        # in fact: ignored, python doesn't have/need them, although a GOTO
        # would consume less memory/cpu by not executing another method ;-)
        data = process_item(fh, cache)
    elif magic_type == '\x14':  # SX_SV_UNDEF    (14): Perl's immortal PL_sv_undef
        print("scalar undef")
    elif magic_type == '\x11':  # SX_BLESS       (17): Object is blessed
        size = unpack('B', fh.read(1))[0]
        package_name = fh.read(size)
        cache['classes'].append(package_name)
        data = process_item(fh, cache)
    elif magic_type == '\x12':  # SX_IX_BLESS    (18): Object is blessed, classname given by index
        indx = unpack('B', fh.read(1))[0]
        package_name = cache['classes'][indx]
        data = process_item(fh, cache)
    elif magic_type == '\x15':  # SX_TIED_KEY    (21): Tied magic key forthcoming
        data = process_item(fh, cache)
        key  = process_item(fh, cache)
    elif magic_type == '\x16':  # SX_TIED_IDX    (22): Tied magic index forthcoming
        data = process_item(fh, cache)
        indx_in_array = unpack('i', fh.read(4))[0]
        
    else:
        return None

    cache['objects'].append(data)
    print(cache)
    return data

