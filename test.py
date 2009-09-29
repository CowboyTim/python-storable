#!/usr/bin/python

import pickle
import glob

from storable import thaw

for infile in sorted(glob.glob('resources/*_nfreeze.storable')):
    # simple test: read data
    print('reading from '+infile)
    infh = open(infile, 'rb')
    data = infh.read()
    infh.close()

    # thaw() it
    data = str(thaw(data))

    # read the to-be-result in
    outfile = infile + '.py'
    outfh = open(outfile,'rb')
    result_we_need = outfh.read()
    outfh.close()

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
    
