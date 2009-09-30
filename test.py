#!/usr/bin/python

import pickle
import glob
import traceback
from re import match
from os.path import basename

from storable import thaw

for infile in sorted(glob.glob('resources/*/*/*_nfreeze.storable')):
    # simple test: read data
    print('reading from '+infile)
    infh = open(infile, 'rb')
    data = infh.read()
    infh.close()

    # thaw() it
    try:
        data = str(thaw(data))
    except Exception,e:
        traceback.print_exc(e)

    result_we_need = None

    # read the to-be-result in
    outfile = basename(infile)
    group = match(r"(.*)_\d+\.\d+", outfile)
    outfile = 'resources/results/' + group.group(1) + '.py'
    try:
        outfh = open(outfile,'rb')
        result_we_need = outfh.read()
        outfh.close()
    except Exception,e:
        traceback.print_exc(e)

    # check
    if result_we_need == data:
        print('OK '+infile)
    else:
        print('NOT OK '+infile)

    # dump it
    if True:
        print('writing output to '+outfile)
        outfh = open(outfile,'wb')
        outfh.write(str(data))
        outfh.close()
    
