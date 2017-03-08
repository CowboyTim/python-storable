from __future__ import print_function

try:
    from itertools import zip_longest
except ImportError:
    zip_longest = None  # We're on Python2

from distutils.version import StrictVersion
from os.path import basename, exists, join
from re import match, search
import glob
import re
import unittest

import storable


P_ID = re.compile(r'[^a-zA-Z0-9]')

src = 'tests/resources'
res = 'tests/results'

__unittest = True  # <- This disables stack traces in unittest output for
                   # everything in this module.


# search for the special tests where the freeze result is not the same as the
# nfreeze result (same for store/nstore). Those tests really do have a seperate
# result file. In such a case, we take the other .store.py file instead of the
# plain .py file as a result to compare with

special_tests = {}
for result in sorted(glob.glob(res + '/*.freeze.py')):
    result = basename(result)
    result = search(r'(.*)\.freeze\.py', result).group(1)
    special_tests[result] = 1


def assertBytesEqual(test_instance, a, b, message):
    """
    Helper method to compare bytes with more helpful output.
    """
    if not isinstance(a, bytes) or not isinstance(b, bytes):
        raise ValueError('assertBytesEqual requires two bytes objects!')

    if not zip_longest:
        # We're on Python 2. Would be nice to re-implement zip_longest. For now,
        # this will have to do.
        test_instance.assertEqual(a, b, message)
        return

    if a != b:
        comparisons = []
        for offset, (char_a, char_b) in enumerate(zip_longest(a, b)):
            comp, marker = ('==', '') if char_a == char_b else ('!=', '>>')

            # Using "zip_longest", overflows are marked as "None", which is
            # unambiguous in this case, but we need to handle these
            # separately from the main format string.
            if char_a is None:
                char_ab = char_ad = char_ah = char_aa = '?'
            else:
                char_ab = '0b{:08b}'.format(char_a)
                char_ad = '{:3d}'.format(char_a)
                char_ah = '0x{:02x}'.format(char_a)
                char_aa = chr(char_a)

            if char_b is None:
                char_bb = char_bd = char_bh = char_ba = '?'
            else:
                char_bb = '0b{:08b}'.format(char_b)
                char_bd = '{:3d}'.format(char_b)
                char_bh = '0x{:02x}'.format(char_b)
                char_ba = chr(char_b)

            comparisons.append(
                "{10:<3} Offset {0:4d}: "
                "{1:^10} {5} {6:^10} | "
                "{2:>3} {5} {7:>3} | "
                "{3:^4} {5} {8:^4} | "
                "{4!r:<6} {5} {9!r:<6}".format(
                    offset,
                    char_ab,
                    char_ad,
                    char_ah,
                    char_aa,
                    comp,
                    char_bb,
                    char_bd,
                    char_bh,
                    char_ba,
                    marker))
        raise AssertionError('Bytes differ (%s)!\n' % message +
                             'type(a)=%s, type(b)=%s\n' % (type(a), type(b)) +
                             '\nIndividual bytes:\n' +
                             '\n'.join(comparisons))


def determine_outfile(storable_fname):
    group = match(r"^(.*)_\d+\.\d+_.*_(freeze|nfreeze|store|nstore)\.storable$",
                  basename(storable_fname))
    testcase = group.group(1)
    freeze = group.group(2)
    if freeze == 'freeze' and testcase in special_tests:
        return res + '/' + testcase + '.freeze.py'
    else:
        return res + '/' + testcase + '.py'


def mythaw(storable_fname):
    infh = open(storable_fname, 'rb')
    data = infh.read()
    infh.close()
    data = storable.thaw(data)
    return data


def myfreeze(obj):
    """
    Not sure if this makes sense (see the comment in storable.py:freeze)
    """
    frozen = storable.freeze(obj)
    return frozen


def make_deserialize_test(deserializer, storable_fname, python_fname):
    def fun(test_instance):

        # If certain files are not found, we dont want to continue the test.
        # "storable_fname" came from "glob" so we don't need to test that.
        # We could also skip the attachment of the unit-test alltogether,
        # but calling ``skipTest`` instead makes it more visible that
        # something was not exeuted and test-runners like pytest can report
        # on this.
        if not exists(python_fname):
            test_instance.skipTest(
                'Expected python file %r not found!' % python_fname)

        # "storable_fname" is the "storable" file which we want to decode.
        data = deserializer(storable_fname)
        assertion_function = test_instance.assertEqual
        try:
            with open(python_fname) as fp:
                code = fp.read()
                compiled = compile(code, python_fname, 'exec')
                expected_scope = {}
                exec(compiled, expected_scope)
                result_we_need = expected_scope['result']
                if 'is_equal' in expected_scope:
                    assertion_function = expected_scope['is_equal']
        except KeyError as exc:
            test_instance.skipTest(
                'File %r should define the variable "result"!' % python_fname)
        except Exception as exc:
            test_instance.skipTest(
                'Unable to compile %r (%s)' % (python_fname, exc))

        # Now we have proper data which we can compare in detail.
        assertion_function(
            data, result_we_need,
            'Deserialisation of %r did not equal the data '
            'given in %r' % (storable_fname, python_fname))
    return fun


def make_serialize_test(serializer, storable_fname, python_fname):
    def fun(test_instance):

        # If certain files are not found, we dont want to continue the test.
        # "storable_fname" came from "glob" so we don't need to test that.
        # We could also skip the attachment of the unit-test alltogether,
        # but calling ``skipTest`` instead makes it more visible that
        # something was not exeuted and test-runners like pytest can report
        # on this.
        if not exists(python_fname):
            test_instance.skipTest(
                'Expected python file %r not found!' % python_fname)

        try:
            with open(python_fname) as fp:
                code = fp.read()
                compiled = compile(code, python_fname, 'exec')
                expected_scope = {}
                exec(compiled, expected_scope)
                python_obj = expected_scope['result']
            data = serializer(python_obj)
        except NotImplementedError as exc:
            test_instance.skipTest(str(exc))

        with open(storable_fname, 'rb') as fp:
            result_we_need = fp.read()

        # Now we have proper data which we can compare in detail.
        test_instance.assertBytesEqual(
            data, result_we_need,
            'Serialisation of %r did not equal the data '
            'given in %r' % (storable_fname, python_fname))
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
        serializer = storable.store
    else:
        deserializer = mythaw
        serializer = myfreeze

    pattern = '*_%s.storable' % type
    storable_files = join(
        source_folder, architecture, storable_version, pattern)

    for storable_fname in sorted(glob.glob(storable_files)):
        # "python_fname" contains our "expected" data:
        python_fname = determine_outfile(storable_fname)

        # create functions which we will attach to the class later on
        deserialize_function_name = 'test_deserialize_%s' % (
            P_ID.sub('_', basename(storable_fname)))
        serialize_function_name = 'test_serialize_%s' % (
            P_ID.sub('_', basename(storable_fname)))

        fun = make_deserialize_test(deserializer, storable_fname, python_fname)
        setattr(cls, deserialize_function_name, fun)

        fun = make_serialize_test(serializer, storable_fname, python_fname)
        setattr(cls, serialize_function_name, fun)


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
    cls.assertBytesEqual = assertBytesEqual

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


class TestSanity(unittest.TestCase):

    def test_package_version(self):
        # The following simply should not raise an exception. We don't want to
        # check for the version number itself. If we did, we'd need to update
        # this check every time we make a new release!
        from storable import __version__
        StrictVersion(__version__)
