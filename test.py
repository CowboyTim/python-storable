#!/usr/bin/python

import unittest
import glob
import traceback
from re import match, search
from os.path import basename

import storable

nr_of_tests = 36
src = 't/resources'

# search for the special tests where the freeze result is not the same as the
# nfreeze result (same for store/nstore). Those tests really do have a seperate
# result file. In such a case, we take the other .store.py file instead of the
# plain .py file as a result to compare with

special_tests = {}
for result in sorted(glob.glob('t/results/*.freeze.py')):
    result = basename(result)
    result = search(r'(.*)\.freeze\.py', result).group(1)
    special_tests[result] = 1

def determine_outfile(infile):
    outfile = basename(infile)
    group = match(r"^(.*)_\d+\.\d+_.*_(freeze|nfreeze|store|nstore)\.storable$", outfile)
    testcase = group.group(1)
    freeze   = group.group(2)
    if freeze == 'freeze' and testcase in special_tests:
        return 't/results/' + testcase + '.freeze.py'
    else:
        return 't/results/' + testcase + '.py'
        
class TestStorable(unittest.TestCase):

    def test_sun4_solaris_nfreeze(self):
        self.run_tests(glob.glob(src+'/sun4-solaris/*/*_nfreeze.storable'))

    def test_ppc_linux_nfreeze(self):
        self.run_tests(glob.glob(src+'/ppc-linux/*/*_nfreeze.storable'), nr=62)

    def test_MSWin32_nfreeze(self):
        self.run_tests(glob.glob(src+'/MSWin32/*/*_nfreeze.storable'))

    def test_x86_64_linux_nfreeze(self):
        self.run_tests(glob.glob(src+'/x86_64-linux/*/*_nfreeze.storable'))

    def test_i686_linux_nfreeze(self):
        self.run_tests(glob.glob(src+'/i686-linux/*/*_nfreeze.storable'))

    def test_x86_64_linux_store(self):
        self.run_tests(glob.glob(src+'/x86_64-linux/*/*_store.storable'), deserializer=lambda f:str(storable.retrieve(f)))

    def test_x86_64_linux_store(self):
        self.run_tests(glob.glob(src+'/x86_64-linux/*/*_nstore.storable'), deserializer=lambda f:str(storable.retrieve(f)))

    def test_freeze(self):
        self.run_tests(glob.glob(src+'/*/*/*_freeze.storable'),nr=206)

    def mythaw(infile):

        #print('reading from infile:'+infile)
        infh = open(infile, 'rb')
        data = infh.read()
        infh.close()

        # thaw() it
        try:
            data = str(storable.thaw(data))
        except Exception,e:
            traceback.print_exc(e)

        return data

    def run_tests(self, files, deserializer=mythaw, nr=nr_of_tests):
        count = 0
        for infile in sorted(files):
            self.do_test(infile, deserializer)
            count = count + 1
        self.assertEqual(count, nr)

    def do_test(self, infile, deserializer):

        data = deserializer(infile)

        result_we_need = None

        # read the to-be-result in
        outfile  = determine_outfile(infile)
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
