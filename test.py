#!/usr/bin/python

from storable import thaw

# simple test: read data
fh = open('/tmp/aaa', 'rb')
data = fh.read()
fh.close()

# thaw() it
data = thaw(data)

# dump it
print(data)
