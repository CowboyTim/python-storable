
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

exclude_for_cache = dict({'\x00': True, '\x0b': True, '\x0c': True, '\x0d': True})

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

    def SX_OBJECT(self):
        # idx's are always big-endian dumped by storable's freeze/nfreeze I think
        i = unpack('>I', self.fh.read(4))[0]
        self.has_sx_object = True
        return (0, i)

    def SX_LSCALAR(self):
        size = unpack(self.size_unpack_fmt, self.fh.read(4))[0]
        return self.fh.read(size)

    def SX_LUTF8STR(self):
        return self.SX_LSCALAR()

    def SX_ARRAY(self):
        size = unpack(self.size_unpack_fmt, self.fh.read(4))[0]
        data = []
        for i in range(0,size):
            data.append(self.process_item())

        return data

    def SX_HASH(self):
        size = unpack(self.size_unpack_fmt, self.fh.read(4))[0]
        data = {}
        for i in range(0,size):
            value = self.process_item()
            size  = unpack(self.size_unpack_fmt, self.fh.read(4))[0]
            key   = self.fh.read(size)
            data[key] = value

        return data

    def SX_REF(self):
        return self.process_item()

    def SX_UNDEF(self):
        return None

    def SX_DOUBLE(self):
        return unpack(self.double_unpack_fmt, self.fh.read(8))[0]

    def SX_BYTE(self):
        return unpack('B', self.fh.read(1))[0] - 128

    def SX_SCALAR(self):
        size = unpack('B', self.fh.read(1))[0]
        return self.fh.read(size)

    def SX_UTF8STR(self):
        return self.SX_SCALAR()

    def SX_TIED_ARRAY(self):
        return self.process_item()

    def SX_TIED_HASH(self):
        return self.SX_TIED_ARRAY()

    def SX_TIED_SCALAR(self):
        return self.SX_TIED_ARRAY()

    def SX_SV_UNDEF(self):
        return None

    def SX_BLESS(self):
        size = unpack('B', self.fh.read(1))[0]
        package_name = self.fh.read(size)
        self.classes.append(package_name)
        return self.process_item()

    def SX_IX_BLESS(self):
        indx = unpack('B', self.fh.read(1))[0]
        package_name = self.classes[indx]
        return self.process_item()

    def SX_OVERLOAD(self):
        return self.process_item()

    def SX_TIED_KEY(self):
        data = self.process_item()
        key  = self.process_item()
        return data
        
    def SX_TIED_IDX(self):
        data = self.process_item()
        # idx's are always big-endian dumped by storable's freeze/nfreeze I think
        indx_in_array = unpack('>I', self.fh.read(4))[0]
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

    def doItem(self, magic_type):
        if   magic_type == '\x00': return self.SX_OBJECT()
        elif magic_type == '\x01': return self.SX_LSCALAR()     # ( 1): Scalar (large binary) follows (length, data)
        elif magic_type == '\x02': return self.SX_ARRAY()       # ( 2): Array forthcoming (size, item list)
        elif magic_type == '\x03': return self.SX_HASH()        # ( 3): Hash forthcoming (size, key/value pair list)
        elif magic_type == '\x04': return self.SX_REF()         # ( 4): Reference to object forthcoming
        elif magic_type == '\x05': return self.SX_UNDEF()       # ( 5): Undefined scalar
        elif magic_type == '\x07': return self.SX_DOUBLE()      # ( 7): Double forthcoming
        elif magic_type == '\x08': return self.SX_BYTE()        # ( 8): (signed) byte forthcoming
        elif magic_type == '\x0a': return self.SX_SCALAR()      # (10): Scalar (binary, small) follows (length, data)
        elif magic_type == '\x0b': return self.SX_TIED_ARRAY()  # (11): Tied array forthcoming
        elif magic_type == '\x0c': return self.SX_TIED_HASH()   # (12): Tied hash forthcoming
        elif magic_type == '\x0d': return self.SX_TIED_SCALAR() # (13): Tied scalar forthcoming
        elif magic_type == '\x0e': return self.SX_SV_UNDEF()    # (14): Perl's immortal PL_sv_undef
        elif magic_type == '\x11': return self.SX_BLESS()       # (17): Object is blessed
        elif magic_type == '\x12': return self.SX_IX_BLESS()    # (18): Object is blessed, classname given by index
        elif magic_type == '\x14': return self.SX_OVERLOAD()    # (20): Overloaded reference
        elif magic_type == '\x15': return self.SX_TIED_KEY()    # (21): Tied magic key forthcoming
        elif magic_type == '\x16': return self.SX_TIED_IDX()    # (22): Tied magic index forthcoming
        elif magic_type == '\x17': return self.SX_UTF8STR()     # (23): UTF-8 string forthcoming (small)
        elif magic_type == '\x18': return self.SX_LUTF8STR()    # (24): UTF-8 string forthcoming (large)
        else:
            raise

    def process_item(self):
        magic_type = self.fh.read(1)
        #print(engine[magic_type])
        if magic_type not in exclude_for_cache:
            i = self.objectnr
            self.objectnr = self.objectnr+1
            data = self.doItem(magic_type)
            self.objects[i] = data
            return data
        else:
            return self.doItem(magic_type)
            
def thaw(frozen_data):
    s = Storable(frozen_data)
    data = s.process_item()

    if s.has_sx_object:
        s.handle_sx_object_refs(data)
    
    return data
