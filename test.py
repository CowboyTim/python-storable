#!/usr/bin/python

import unittest
import glob
import traceback
from re import match, search
from os.path import basename

from storable import thaw

class TestStorable(unittest.TestCase):

    def test_sun4_solaris_nfreeze(self):
        for infile in sorted(glob.glob('t/resources/sun4-solaris/*/*_nfreeze.storable')):
            self.do_test(infile)

    def test_ppc_linux_nfreeze(self):
        for infile in sorted(glob.glob('t/resources/ppc-linux/*/*_nfreeze.storable')):
            self.do_test(infile)

    def test_MSWin32_nfreeze(self):
        for infile in sorted(glob.glob('t/resources/MSWin32/*/*_nfreeze.storable')):
            self.do_test(infile)

    def test_x86_64_linux_nfreeze(self):
        for infile in sorted(glob.glob('t/resources/x86_64-linux/*/*_nfreeze.storable')):
            self.do_test(infile)

    def test_i686_linux_nfreeze(self):
        for infile in sorted(glob.glob('t/resources/i686-linux/*/*_nfreeze.storable')):
            self.do_test(infile)

    def test_ppc_linux_freeze(self):
        for infile in sorted(glob.glob('t/resources/ppc-linux/*/*_freeze.storable')):
            m = search(r'(017|021|023|025|027|029|045|053)_', infile)
            if m == None:
                outfile = basename(infile)
                group = match(r"^(\d+)_(.*)_\d+\.\d+_.*_(freeze|nfreeze)\.storable$", outfile)
                type       = group.group(3)
                testcasenr = int(group.group(1))+1
                testcase   = group.group(2)
                outfile    = 't/results/' + '%03d'%testcasenr + '_' + testcase + '.py'
                self.do_test(infile, outfile)

    def test_ppc_linux_freeze_special_cases(self):
        for infile in sorted(glob.glob('t/resources/ppc-linux/*/*_freeze.storable')):
            m = search(r'(017|021|023|025|027|029|045|053)_', infile)
            if m != None:
                self.do_test(infile)

    def load_objects(self, infile, outfile=None):

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
        if not outfile:
            outfile = basename(infile)
            group = match(r"^(.*)_\d+\.\d+_.*_(freeze|nfreeze)\.storable$", outfile)
            testcase = group.group(1)
            outfile  = 't/results/' + testcase + '.py'
        try:
            outfh = open(outfile,'rb')
            result_we_need = outfh.read()
            #print(str(result_we_need))
            outfh.close()
        except Exception,e:
            traceback.print_exc(e)

        return (outfile, result_we_need, data)

    def do_test(self, infile, outfile=None):

        outfile, result_we_need, data = self.load_objects(infile, outfile)

        # dump it
        if False:
            #print('writing output to '+outfile)
            outfh = open(outfile,'wb')
            outfh.write(data)
            outfh.close()

        # check
        try:
            self.assertEqual(data, result_we_need)
        except AssertionError, e:
            print('FILE: '+infile)
            raise e

    
suite = unittest.TestLoader().loadTestsFromTestCase(TestStorable)
unittest.TextTestRunner(verbosity=2).run(suite)
