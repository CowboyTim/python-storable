from __future__ import print_function

from os.path import basename, exists, join
from re import match, search
import glob
import re
import unittest

import storable


P_ID = re.compile(r'[^a-zA-Z0-9]')

src = 'tests/resources'
res = 'tests/results'


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
    infh = open(infile, 'rb')
    data = infh.read()
    infh.close()
    data = storable.thaw(data)
    return data


def make_function(deserializer, infile, outfile):
    def fun(test_instance):

        # If certain files are not found, we dont want to continue the test.
        # "infile" came from "glob" so we don't need to test that.
        # We could also skip the attachment of the unit-test alltogether,
        # but calling ``skipTest`` instead makes it more visible that
        # something was not exeuted and test-runners like pytest can report
        # on this.
        if not exists(outfile):
            test_instance.skipTest(
                'Expected output file %r not found!' % outfile)

        # "infile" is to "storable" file which we want to decode.
        data = deserializer(infile)
        try:
            with open(outfile) as fp:
                code = fp.read()
                compiled = compile(code, outfile, 'exec')
                expected_scope = {}
                exec(compiled, expected_scope)
                result_we_need = expected_scope['result']
        except KeyError as exc:
            test_instance.skipTest(
                'File %r should define the variable "result"!' % outfile)
        except Exception as exc:
            test_instance.skipTest(
                'Unable to compile %r (%s)' % (outfile, exc))

        # Now we have proper data which we can compare in detail.
        test_instance.assertEqual(
            data, result_we_need,
            'Deserialisation of %r did not equal the data '
            'given in %r' % (infile, outfile))
    return fun


def attach_tests(cls, source_folder, architecture, storable_version, type):
    """
    Creates unit-tests based on the files found in ``source_folder``.

    For each input (storable) file we find in the subfolder (based on
    *architecture*, *storable_version* and "*type*" of storable) we create
    unit-test functions and attach them to the ``TestCase`` class given via
    *cls*.
    """
    if type in ['store', 'nstore']:
        deserializer = storable.retrieve
    else:
        deserializer = mythaw

    pattern = '*_%s.storable' % type
    files = join(source_folder, architecture, storable_version, pattern)

    for infile in sorted(glob.glob(files)):
        # "outfile" contains our "expected" data:
        outfile = determine_outfile(infile)

        # create a function which we will attach to the class later on
        function_name = 'test_%s' % (P_ID.sub('_', basename(infile)))
        fun = make_function(deserializer, infile, outfile)

        # now that the function is defined, we can attach it to the test-class.
        setattr(cls, function_name, fun)


# A list of architectures with an array of versions we want to test against.
architectures = [
    ('MSWin32', ['2.15']),
    ('i386-darwin', ['2.19']),
    ('i686-linux', ['2.15']),
    ('ppc-linux', ['2.18', '2.20', '2.21']),
    ('ppc64-linux', ['2.21']),
    ('sun4-solaris', ['2.08']),
    ('x86_64-linux', ['2.18', '2.19', '2.21', '2.29', '2.41'])
]


for arch, supported_versions in architectures:
    # Dynamically create a class (one class per architecture)
    # This creates a subclass of "unittest.TestCase" which will later be
    # injected to the globals. It avoids having to create tedious tests manually
    # while still giving us atomic unit-tests for each specific case and hence
    # much more usable error-output in case of failure.
    clsname = 'Test%s' % P_ID.sub('_', arch).capitalize()
    cls = type(clsname, (unittest.TestCase,), {})

    # Attach test functions
    for version in supported_versions:
        attach_tests(cls, src, arch, version, 'freeze')
        attach_tests(cls, src, arch, version, 'nfreeze')
        attach_tests(cls, src, arch, version, 'store')
        attach_tests(cls, src, arch, version, 'nstore')

    # Make the class available in the global scope (for test discovery)
    globals()[clsname] = cls

    # Remove the temporarily created class from the global scope (to avoid
    # duplicate discovery)
    del(cls)
