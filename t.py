#!/usr/bin/python

import storable

fh = open("t/resources/x86_64-linux/2.18/050_complex06_2.18_x86_64-linux_nfreeze.storable", "rb")
small_data = fh.read()
fh.close()

fh = open("t/large_simple01.storable", "rb")
large_data = fh.read()
fh.close()

def timethese(nr, methods):
    for k,method in methods.iteritems():
        print("doing: "+k)
        for i in range(0,nr):
            method()

timethese(10, {
    'small' : lambda :storable.thaw(small_data),
    'large' : lambda :storable.thaw(large_data)
})
