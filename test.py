#!/usr/bin/python

import glob

from storable import thaw

for f in glob.glob('/python-storable/resources/*nfreeze.storable'):
    print(f)
    # simple test: read data
    fh = open(f, 'rb')
    data = fh.read()
    fh.close()

    # thaw() it
    data = thaw(data)

    # dump it
    print(data)
