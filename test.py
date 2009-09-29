#!/usr/bin/python

import pickle
import glob

from storable import thaw

for infile in glob.glob('resources/*nfreeze.storable'):
    # simple test: read data
    print('reading from '+infile)
    infh = open(infile, 'rb')
    data = infh.read()
    infh.close()

    # thaw() it
    data = thaw(data)

    # dump it
    outfile = infile + '.pickle'
    print('writing output to '+outfile)
    outfh = open(outfile,'wb')
    pickle.dump(data, outfh)
    outfh.close()
    
    print(data)
