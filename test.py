#!/usr/bin/python

import unittest
import glob
import traceback
from re import match, search
from os.path import basename

import storable

nr_of_tests = 36

expected = {
    'ppc64-linux'   : {
        '2.21' : { 
            'nfreeze' : nr_of_tests + 9,
            'freeze'  : nr_of_tests + 9,
            'store'   : nr_of_tests + 9,
            'nstore'  : nr_of_tests + 9
        }
    },
    'i386-darwin'   : {
        '2.19' : { 
            'nfreeze' : nr_of_tests,
            'freeze'  : nr_of_tests,
            'store'   : nr_of_tests,
            'nstore'  : nr_of_tests
        }
    },
    'i686-linux'   : {
        '2.15' : { 
            'nfreeze' : nr_of_tests,
            'freeze'  : nr_of_tests,
            'store'   : 0,
            'nstore'  : 0
        }
    },
    'MSWin32'      : {
        '2.15' : { 
            'nfreeze' : nr_of_tests,
            'freeze'  : nr_of_tests,
            'store'   : 0,
            'nstore'  : 0
        }
    },
    'ppc-linux'    : {
        '2.18' : { 
            'nfreeze' : nr_of_tests + 9,
            'freeze'  : nr_of_tests + 9,
            'store'   : nr_of_tests + 9,
            'nstore'  : nr_of_tests + 9
        },
        '2.20' : { 
            'nfreeze' : nr_of_tests + 9,
            'freeze'  : nr_of_tests + 9,
            'store'   : nr_of_tests + 9,
            'nstore'  : nr_of_tests + 9
        },
        '2.21' : { 
            'nfreeze' : nr_of_tests + 9,
            'freeze'  : nr_of_tests + 9,
            'store'   : nr_of_tests + 9,
            'nstore'  : nr_of_tests + 9
        }
    },
    'sun4-solaris' : {
        '2.08' : { 
            'nfreeze' : nr_of_tests,
            'freeze'  : nr_of_tests,
            'store'   : 0,
            'nstore'  : 0
        }
    },
    'x86_64-linux' : {
        '2.18' : { 
            'nfreeze' : nr_of_tests + 9,
            'freeze'  : nr_of_tests + 9,
            'store'   : nr_of_tests + 9,
            'nstore'  : nr_of_tests + 9
        },
        '2.21' : { 
            'nfreeze' : nr_of_tests,
            'freeze'  : nr_of_tests,
            'store'   : nr_of_tests,
            'nstore'  : nr_of_tests
        },
        '2.19' : { 
            'nfreeze' : nr_of_tests + 9,
            'freeze'  : nr_of_tests + 9,
            'store'   : nr_of_tests + 9,
            'nstore'  : nr_of_tests + 9
        },
        '2.29' : {
            'nfreeze' : nr_of_tests + 9,
            'freeze'  : nr_of_tests + 9,
            'store'   : nr_of_tests + 9,
            'nstore'  : nr_of_tests + 9
        }
    },
}

src = 't/resources'
res = 't/results'

# search for the special tests where the freeze result is not the same as the
# nfreeze result (same for store/nstore). Those tests really do have a seperate
# result file. In such a case, we take the other .store.py file instead of the
# plain .py file as a result to compare with

special_tests = {}
for result in sorted(glob.glob(res + '/*.freeze.py')):
    result = basename(result)
    result = search(r'(.*)\.freeze\.py', result).group(1)
    special_tests[result] = 1

def determine_outfile(infile):
    outfile = basename(infile)
    group = match(r"^(.*)_\d+\.\d+_.*_(freeze|nfreeze|store|nstore)\.storable$", outfile)
    testcase = group.group(1)
    freeze   = group.group(2)
    if freeze == 'freeze' and testcase in special_tests:
        return res + '/' + testcase + '.freeze.py'
    else:
        return res + '/' + testcase + '.py'

def mythaw(infile):
    #print('reading from infile:'+infile)
    infh = open(infile, 'rb')
    data = infh.read()
    infh.close()

    # thaw() it
    try:
        data = storable.thaw(data)
    except Exception,e:
        traceback.print_exc(e)

    return data

        
class TestStorable(unittest.TestCase):

    #
    def test_ppc64_linux_2_21_nfreeze(self):
        self.run_tests('ppc64-linux', '2.21', 'nfreeze')
    def test_ppc64_linux_2_21_freeze(self):
        self.run_tests('ppc64-linux', '2.21', 'freeze')
    def test_ppc64_linux_2_21_nstore(self):
        self.run_tests('ppc64-linux', '2.21', 'nstore')
    def test_ppc64_linux_2_21_store(self):
        self.run_tests('ppc64-linux', '2.21', 'store')

    #
    def test_i386_darwin_2_19_nfreeze(self):
        self.run_tests('i386-darwin', '2.19', 'nfreeze')
    def test_i386_darwin_2_19_freeze(self):
        self.run_tests('i386-darwin', '2.19', 'freeze')
    def test_i386_darwin_2_19_nstore(self):
        self.run_tests('i386-darwin', '2.19', 'nstore')
    def test_i386_darwin_2_19_store(self):
        self.run_tests('i386-darwin', '2.19', 'store')

    #
    def test_i686_linux_2_15_nfreeze(self):
        self.run_tests('i686-linux', '2.15', 'nfreeze')
    def test_i686_linux_2_15_freeze(self):
        self.run_tests('i686-linux', '2.15', 'freeze')
    def test_i686_linux_2_15_nstore(self):
        self.run_tests('i686-linux', '2.15', 'nstore')
    def test_i686_linux_2_15_store(self):
        self.run_tests('i686-linux', '2.15', 'store')

    #
    def test_MSWin32_2_15_nfreeze(self):
        self.run_tests('MSWin32', '2.15', 'nfreeze')
    def test_MSWin32_2_15_freeze(self):
        self.run_tests('MSWin32', '2.15', 'freeze')
    def test_MSWin32_2_15_nstore(self):
        self.run_tests('MSWin32', '2.15', 'nstore')
    def test_MSWin32_2_15_store(self):
        self.run_tests('MSWin32', '2.15', 'store')

    #
    def test_ppc_linux_2_18_nfreeze(self):
        self.run_tests('ppc-linux', '2.18', 'nfreeze')
    def test_ppc_linux_2_18_freeze(self):
        self.run_tests('ppc-linux', '2.18', 'freeze')
    def test_ppc_linux_2_18_nstore(self):
        self.run_tests('ppc-linux', '2.18', 'nstore')
    def test_ppc_linux_2_18_store(self):
        self.run_tests('ppc-linux', '2.18', 'store')

    #
    def test_ppc_linux_2_20_nfreeze(self):
        self.run_tests('ppc-linux', '2.20', 'nfreeze')
    def test_ppc_linux_2_20_freeze(self):
        self.run_tests('ppc-linux', '2.20', 'freeze')
    def test_ppc_linux_2_20_nstore(self):
        self.run_tests('ppc-linux', '2.20', 'nstore')
    def test_ppc_linux_2_20_store(self):
        self.run_tests('ppc-linux', '2.20', 'store')

    #
    def test_ppc_linux_2_21_nfreeze(self):
        self.run_tests('ppc-linux', '2.21', 'nfreeze')
    def test_ppc_linux_2_21_freeze(self):
        self.run_tests('ppc-linux', '2.21', 'freeze')
    def test_ppc_linux_2_21_nstore(self):
        self.run_tests('ppc-linux', '2.21', 'nstore')
    def test_ppc_linux_2_21_store(self):
        self.run_tests('ppc-linux', '2.21', 'store')

    #
    def test_sun4_solaris_2_08_nfreeze(self):
        self.run_tests('sun4-solaris', '2.08', 'nfreeze')
    def test_sun4_solaris_2_08_freeze(self):
        self.run_tests('sun4-solaris', '2.08', 'freeze')
    def test_sun4_solaris_2_08_nstore(self):
        self.run_tests('sun4-solaris', '2.08', 'nstore')
    def test_sun4_solaris_2_08_store(self):
        self.run_tests('sun4-solaris', '2.08', 'store')

    #
    def test_x86_64_linux_2_18_nfreeze(self):
        self.run_tests('x86_64-linux', '2.18', 'nfreeze')
    def test_x86_64_linux_2_18_freeze(self):
        self.run_tests('x86_64-linux', '2.18', 'freeze')
    def test_x86_64_linux_2_18_nstore(self):
        self.run_tests('x86_64-linux', '2.18', 'nstore')
    def test_x86_64_linux_2_18_store(self):
        self.run_tests('x86_64-linux', '2.18', 'store')

    #
    def test_x86_64_linux_2_21_nfreeze(self):
        self.run_tests('x86_64-linux', '2.21', 'nfreeze')
    def test_x86_64_linux_2_21_freeze(self):
        self.run_tests('x86_64-linux', '2.21', 'freeze')
    def test_x86_64_linux_2_21_nstore(self):
        self.run_tests('x86_64-linux', '2.21', 'nstore')
    def test_x86_64_linux_2_21_store(self):
        self.run_tests('x86_64-linux', '2.21', 'store')

    #
    def test_x86_64_linux_2_19_nfreeze(self):
        self.run_tests('x86_64-linux', '2.19', 'nfreeze')
    def test_x86_64_linux_2_19_freeze(self):
        self.run_tests('x86_64-linux', '2.19', 'freeze')
    def test_x86_64_linux_2_19_nstore(self):
        self.run_tests('x86_64-linux', '2.19', 'nstore')
    def test_x86_64_linux_2_19_store(self):
        self.run_tests('x86_64-linux', '2.19', 'store')

    #
    def test_x86_64_linux_2_29_nfreeze(self):
        self.run_tests('x86_64-linux', '2.29', 'nfreeze')
    def test_x86_64_linux_2_29_freeze(self):
        self.run_tests('x86_64-linux', '2.29', 'freeze')
    def test_x86_64_linux_2_29_nstore(self):
        self.run_tests('x86_64-linux', '2.29', 'nstore')
    def test_x86_64_linux_2_29_store(self):
        self.run_tests('x86_64-linux', '2.29', 'store')

    def run_tests(self, architecture, storableversion, type):
        d = mythaw
        if type in ['store', 'nstore']:
            d = storable.retrieve
        nr_tests = expected[architecture][storableversion][type]
        files = src+'/'+architecture+'/'+storableversion+'/*_'+type+'.storable'
        count = 0
        for infile in sorted(glob.glob(files)):
            self.do_test(infile, deserializer=d)
            count = count + 1
        self.assertEqual(count, nr_tests)

    def do_test(self, infile, deserializer):

        data = deserializer(infile)

        result_we_need = None

        # read the to-be-result in
        outfile = determine_outfile(infile)
        try:
            outfh = open(outfile,'rb')
            result_we_need = outfh.read()
            #print(str(result_we_need))
            outfh.close()
        except Exception,e:
            traceback.print_exc(e)

        # dump it
        if True:
            #print('writing output to '+outfile)
            outfh = open(outfile,'wb')
            outfh.write(str(data))
            outfh.close()

        # check
        try:
            self.assertEqual(str(data), str(result_we_need))
        except AssertionError, e:
            print('infile: '+str(infile)+' ,outfile: '+str(outfile))
            raise e

suite = unittest.TestLoader().loadTestsFromTestCase(TestStorable)
unittest.TextTestRunner(verbosity=2).run(suite)
