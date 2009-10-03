#!/usr/bin/python

import unittest
import glob
import traceback
from re import match
from os.path import basename

from storable import thaw

class TestStorable(unittest.TestCase):

    def test_sun4_solaris_nfreeze(self):
        for infile in sorted(glob.glob('resources/sun4-solaris/*/*_nfreeze.storable')):
            self.do_test(infile)

    def test_ppc_linux_nfreeze(self):
        for infile in sorted(glob.glob('resources/ppc-linux/*/*_nfreeze.storable')):
            self.do_test(infile)

    def test_MSWin32_nfreeze(self):
        for infile in sorted(glob.glob('resources/MSWin32/*/*_nfreeze.storable')):
            self.do_test(infile)

    def test_x86_64_linux_nfreeze(self):
        for infile in sorted(glob.glob('resources/x86_64-linux/*/*_nfreeze.storable')):
            self.do_test(infile)

    def test_i686_linux_nfreeze(self):
        for infile in sorted(glob.glob('resources/i686-linux/*/*_nfreeze.storable')):
            self.do_test(infile)

    def test_circular(self):
        for tc in ['052_complex07', '050_complex06', '048_complex05']:
            for infile in sorted(glob.glob('resources/*/*/'+tc+'*_nfreeze.storable')):
                testcase, outfile, result_we_need, data = self.load_objects(infile)
                print(testcase)
                try:
                    self.assertEqual(data, result_we_need)
                except AssertionError, e:
                    print('FILE: '+infile)
                    raise e

    def load_objects(self, infile):

        #print('reading from '+infile)
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
            #print(str(result_we_need))
            outfh.close()
        except Exception,e:
            traceback.print_exc(e)

        return (testcase, outfile, result_we_need, data)

    def do_test(self, infile):

        testcase, outfile, result_we_need, data = self.load_objects(infile)

        # check
        if      testcase != '048_complex05' \
            and testcase != '050_complex06' \
            and testcase != '052_complex07':
            try:
                self.assertEqual(data, result_we_need)
            except AssertionError, e:
                print('FILE: '+infile)
                raise e

        # dump it
        if False:
            #print('writing output to '+outfile)
            outfh = open(outfile,'wb')
            outfh.write(str(data))
            outfh.close()
    
suite = unittest.TestLoader().loadTestsFromTestCase(TestStorable)
unittest.TextTestRunner(verbosity=2).run(suite)
