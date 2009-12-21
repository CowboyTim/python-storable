#!/usr/bin/python

import unittest
import glob
import traceback
from re import match, search
from os.path import basename

import storable

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

    def test_x86_64_linux_store(self):
        for infile in sorted(glob.glob('t/resources/x86_64-linux/*/*_store.storable')):
            self.do_test(infile, deserializer=lambda f:str(storable.retrieve(f)))

    def test_freeze(self):
        special_tests = {}
        for result in sorted(glob.glob('t/results/*.freeze.py')):
            result = basename(result)
            result = search(r'(.*)\.freeze\.py', result).group(1)
            special_tests[result] = 1

        for infile in sorted(glob.glob('t/resources/*/*/*_freeze.storable')):
            outfile = basename(infile)
            group = match(r"^(.*)_\d+\.\d+_.*_(freeze|nfreeze)\.storable$", outfile)
            testcase = group.group(1)
            if testcase not in special_tests:
                outfile  = 't/results/' + testcase + '.py'
                self.do_test(infile, outfile)

    def test_freeze_special_cases(self):
        special_tests = {}
        for result in sorted(glob.glob('t/results/*.freeze.py')):
            result = basename(result)
            result = search(r'(.*)\.freeze\.py', result).group(1)
            special_tests[result] = 1

        for infile in sorted(glob.glob('t/resources/*/*/*_freeze.storable')):
            outfile = basename(infile)
            group = match(r"^(.*)_\d+\.\d+_.*_(freeze|nfreeze)\.storable$", outfile)
            testcase = group.group(1)
            if testcase in special_tests:
                outfile  = 't/results/' + testcase + '.freeze.py'
                self.do_test(infile, outfile)

    def mythaw(infile):

        print('reading from infile:'+infile)
        infh = open(infile, 'rb')
        data = infh.read()
        infh.close()

        # thaw() it
        try:
            data = str(storable.thaw(data))
        except Exception,e:
            traceback.print_exc(e)

        return data

    def do_test(self, infile, outfile=None, deserializer=mythaw):

        data = deserializer(infile)

        result_we_need = None

        # read the to-be-result in
        if not outfile:
            outfile = basename(infile)
            group = match(r"^(.*)_\d+\.\d+_.*_(freeze|nfreeze|store|nstore)\.storable$", outfile)
            testcase = group.group(1)
            outfile  = 't/results/' + testcase + '.py'
        try:
            outfh = open(outfile,'rb')
            result_we_need = outfh.read()
            #print(str(result_we_need))
            outfh.close()
        except Exception,e:
            traceback.print_exc(e)

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
            print('infile: '+str(infile)+' ,outfile: '+str(outfile))
            raise e

    
suite = unittest.TestLoader().loadTestsFromTestCase(TestStorable)
unittest.TextTestRunner(verbosity=2).run(suite)
