
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
import cStringIO

exclude_for_cache = set(['\x00', '\x0b', '\x0c', '\x0d'])

class Storable():

    def __init__(self, frozen_data):
        fh    = cStringIO.StringIO(frozen_data)
        magic = fh.read(1)
        byteorder = '>'
        if magic == '\x05':
            version = fh.read(1)
            #print("OK:nfreeze") 
            pass
        if magic == '\x04':
            version = fh.read(1)
            size  = unpack('B', fh.read(1))[0]
            byteorder = fh.read(size)
            #print("OK:freeze:" + str(byteorder))

            # 32-bit ppc:     4321
            # 32-bit x86:     1234
            # 64-bit x86_64:  12345678
            
            if byteorder == '1234' or byteorder == '12345678':
                byteorder = '<'
            else:
                byteorder = '>'

            somethingtobeinvestigated = fh.read(4)

        self.objectnr          = 0
        self.objects           = {}
        self.classes           = []
        self.has_sx_object     = False
        self.size_unpack_fmt   = byteorder + 'I'
        self.double_unpack_fmt = byteorder + 'd'
        self.fh                = fh

    def SX_OBJECT(self,fh):
        # idx's are always big-endian dumped by storable's freeze/nfreeze I think
        i = unpack('>I', fh.read(4))[0]
        self.has_sx_object = True
        return (0, i)

    def SX_LSCALAR(self,fh):
        size = unpack(self.size_unpack_fmt, fh.read(4))[0]
        return fh.read(size)

    def SX_LUTF8STR(self,fh):
        return self.SX_LSCALAR(fh)

    def SX_ARRAY(self,fh):
        size = unpack(self.size_unpack_fmt, fh.read(4))[0]
        data = []
        for i in range(0,size):
            data.append(self.process_item(fh))

        return data

    def SX_HASH(self,fh):
        size = unpack(self.size_unpack_fmt, fh.read(4))[0]
        data = {}
        for i in range(0,size):
            value = self.process_item(fh)
            size  = unpack(self.size_unpack_fmt, fh.read(4))[0]
            key   = fh.read(size)
            data[key] = value

        return data

    def SX_REF(self,fh):
        return self.process_item(fh)

    def SX_UNDEF(self,fh):
        return None

    def SX_DOUBLE(self,fh):
        return unpack(self.double_unpack_fmt, fh.read(8))[0]

    def SX_BYTE(self,fh):
        return unpack('B', fh.read(1))[0] - 128

    def SX_SCALAR(self,fh):
        size = unpack('B', fh.read(1))[0]
        return fh.read(size)

    def SX_UTF8STR(self,fh):
        return self.SX_SCALAR(fh)

    def SX_TIED_ARRAY(self,fh):
        return self.process_item(fh)

    def SX_TIED_HASH(self,fh):
        return self.SX_TIED_ARRAY(fh)

    def SX_TIED_SCALAR(self,fh):
        return self.SX_TIED_ARRAY(fh)

    def SX_SV_UNDEF(self,fh):
        return None

    def SX_BLESS(self,fh):
        size = unpack('B', fh.read(1))[0]
        package_name = fh.read(size)
        self.classes.append(package_name)
        return self.process_item(fh)

    def SX_IX_BLESS(self,fh):
        indx = unpack('B', fh.read(1))[0]
        package_name = self.classes[indx]
        return self.process_item(fh)

    def SX_OVERLOAD(self,fh):
        return self.process_item(fh)

    def SX_TIED_KEY(self,fh):
        data = self.process_item(fh)
        key  = self.process_item(fh)
        return data
        
    def SX_TIED_IDX(self,fh):
        data = self.process_item(fh)
        # idx's are always big-endian dumped by storable's freeze/nfreeze I think
        indx_in_array = unpack('>I', fh.read(4))[0]
        return data

    def handle_sx_object_refs(self, data):
        iterateelements = None
        if type(data) is list:
            iterateelements = enumerate(iter(data))
        elif type(data) is dict:
            iterateelements = data.iteritems()
        else:
            return
        
        for k,item in iterateelements:
            if type(item) is list or type(item) is dict:
                self.handle_sx_object_refs(item)
            if type(item) is tuple:
                data[k] = self.objects[item[1]]
        return data

    def process_item(self, fh):
        magic_type = fh.read(1)
        if magic_type in engine:
            #print(engine[magic_type])
            if magic_type not in exclude_for_cache:
                i = self.objectnr
                self.objectnr = self.objectnr+1
                data = engine[magic_type](self,fh)
                self.objects[i] = data
                return data
            else:
                data = engine[magic_type](self,fh)
                return data
            
def thaw(frozen_data):
    s = Storable(frozen_data)
    data = s.process_item(s.fh)

    if s.has_sx_object:
        s.handle_sx_object_refs(data)
    
    return data

engine = {
    '\x00': Storable.SX_OBJECT,      # ( 0): Already stored object
    '\x01': Storable.SX_LSCALAR,     # ( 1): Scalar (large binary) follows (length, data)
    '\x02': Storable.SX_ARRAY,       # ( 2): Array forthcoming (size, item list)
    '\x03': Storable.SX_HASH,        # ( 3): Hash forthcoming (size, key/value pair list)
    '\x04': Storable.SX_REF,         # ( 4): Reference to object forthcoming
    '\x05': Storable.SX_UNDEF,       # ( 5): Undefined scalar
    '\x07': Storable.SX_DOUBLE,      # ( 7): Double forthcoming
    '\x08': Storable.SX_BYTE,        # ( 8): (signed) byte forthcoming
    '\x0a': Storable.SX_SCALAR,      # (10): Scalar (binary, small) follows (length, data)
    '\x0b': Storable.SX_TIED_ARRAY,  # (11): Tied array forthcoming
    '\x0c': Storable.SX_TIED_HASH,   # (12): Tied hash forthcoming
    '\x0d': Storable.SX_TIED_SCALAR, # (13): Tied scalar forthcoming
    '\x0e': Storable.SX_SV_UNDEF,    # (14): Perl's immortal PL_sv_undef
    '\x11': Storable.SX_BLESS,       # (17): Object is blessed
    '\x12': Storable.SX_IX_BLESS,    # (18): Object is blessed, classname given by index
    '\x14': Storable.SX_OVERLOAD,    # (20): Overloaded reference
    '\x15': Storable.SX_TIED_KEY,    # (21): Tied magic key forthcoming
    '\x16': Storable.SX_TIED_IDX,    # (22): Tied magic index forthcoming
    '\x17': Storable.SX_UTF8STR,     # (23): UTF-8 string forthcoming (small)
    '\x18': Storable.SX_LUTF8STR,    # (24): UTF-8 string forthcoming (large)
}



