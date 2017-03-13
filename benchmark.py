#!/usr/bin/python

from time import time

import storable


def timethese(nr, methods):
    print('Benchmark: timing {} iterations of {}...'.format(
        nr, ', '.join(methods)))
    for k, method in methods.items():
        start = time()
        for i in range(nr):
            method()
        end = time()
        print(
            '%(abbr)15s : %(timing)7.2f wallclock secs @ %(speed).02f/s (n=%(nr)d)'
            % {'abbr': k,
               'timing': (end - start),
               'speed': (end - start) / nr,
               'nr': nr}
        )



def run():
    with open("tests/resources/x86_64-linux/2.18/025_complex06_2.18_x86_64-linux_nfreeze.storable", "rb") as fh:
        small_data_nfreeze = fh.read()

    with open("tests/resources/x86_64-linux/2.18/025_complex06_2.18_x86_64-linux_freeze.storable", "rb") as fh:
        small_data_freeze = fh.read()

    with open("tests/large_simple01_nfreeze.storable", "rb") as fh:
        large_data_nfreeze = fh.read()

    with open("tests/large_simple01_freeze.storable", "rb") as fh:
        large_data_freeze = fh.read()

    timethese(100, {
        'small_nfreeze': lambda: storable.thaw(small_data_nfreeze),
        'small_freeze': lambda: storable.thaw(small_data_freeze),
        'large_nfreeze': lambda: storable.thaw(large_data_nfreeze),
        'large_freeze': lambda: storable.thaw(large_data_freeze)
    })

#import cProfile
#cProfile.run('run()')
# import threading
# tl = []
# for i in range(0,4):
#     print("making thread:"+str(i))
#     t = threading.Thread(target=run,args=())
#     t.start()
#     tl.append(t)
#
# for t in tl:
#     t.join()
run()
