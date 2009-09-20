#!/usr/bin/python

from storable import thaw

# simple test
fh = open('/tmp/aaa', 'rb')
data = thaw(fh)
print(data)
#data['dd'] = 'y'
#data['cc']['yy'] = 'y'
#print(data)

fh.close()
