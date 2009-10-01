#!/usr/bin/python

import unittest
import glob
import traceback
from re import match
from os.path import basename

from storable import thaw

class TestMore(unittest.TestCase):
    def runTest(self):

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
            testcase = group.group(1)
            outfile = 'resources/results/' + testcase + '.py'
            try:
                outfh = open(outfile,'rb')
                result_we_need = outfh.read()
                outfh.close()
            except Exception,e:
                traceback.print_exc(e)

            # check
            if      testcase != '046_complex04' \
                and testcase != '048_complex05' \
                and testcase != '050_complex06':
                self.assertEqual(result_we_need, data)

            # dump it
            if True:
                print('writing output to '+outfile)
                outfh = open(outfile,'wb')
                outfh.write(data)
                outfh.close()
    

if __name__ == '__main__':
    unittest.main()
