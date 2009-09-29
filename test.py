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
    data = thaw(data)

    # dump it
    outfile = infile + '.py'
    print('writing output to '+outfile)
    outfh = open(outfile,'wb')
    outfh.write(str(data))
    outfh.close()
    
