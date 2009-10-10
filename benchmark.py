#!/usr/bin/python

from time import time
import storable

fh = open("t/resources/x86_64-linux/2.18/050_complex06_2.18_x86_64-linux_nfreeze.storable", "rb")
small_data_nfreeze = fh.read()
fh.close()

fh = open("t/resources/x86_64-linux/2.18/049_complex06_2.18_x86_64-linux_freeze.storable", "rb")
small_data_freeze = fh.read()
fh.close()

fh = open("t/large_simple01_nfreeze.storable", "rb")
large_data_nfreeze = fh.read()
fh.close()

fh = open("t/large_simple01_freeze.storable", "rb")
large_data_freeze = fh.read()
fh.close()

def timethese(nr, methods):
    print('Benchmark: timing '+str(nr)+' iterations of '+', '.join(methods.iterkeys())+'...')
    for k,method in methods.iteritems():
        start = time()
        for i in range(0,nr):
            method()
        end   = time()
        print('%(abbr)15s : %(timing)7.2f wallclock secs @ %(speed).02f/s (n=%(nr)d)'\
                %{'abbr'  :k,\
                  'timing':(end - start),\
                  'speed' :(end - start)/nr,\
                  'nr'    :nr})


def run():
    timethese(100, {
        'small_nfreeze' : lambda :storable.thaw(small_data_nfreeze),
        'small_freeze'  : lambda :storable.thaw(small_data_freeze ),
        'large_nfreeze' : lambda :storable.thaw(large_data_nfreeze),
        'large_freeze'  : lambda :storable.thaw(large_data_freeze )
    })

#import cProfile
#cProfile.run('run()')
run()
