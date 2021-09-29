
python-storable
===============

.. image:: https://raster.shields.io/pypi/v/storable
    :target: https://pypi.org/project/storable/
.. image:: https://raster.shields.io/travis/CowboyTim/python-storable/master
    :target: https://travis-ci.com/github/CowboyTim/python-storable

Overview
--------

This is a Python module that is be able to read Perl storable files. Storable
is a nice and efficient binary format for Perl that is very popular. A lot of
other serialization/deserialization modules exist that are even more or less
standardized: JSON, XML, CSV,.. etc. Storable is more or less Perl specific.

To ease integration between Perl - where storable sometimes is the only option
- and Python this module is a bridge.

The module has been tested to work with Python 2.7 and upwards.


.. warning:: **Perl Scalar Handling**

    Care has to be taken when dealing with Perl "scalars". They are a bit
    "magical" in that they can behave like different types depending on how
    they are used. This is currently not supported directly in Python, and
    **neither does this library provide a suitable abstraction!**

    The way this is currently handled is that types are "guessed" in a fairly
    iffy manner! The value is tried to be converted to different types (at the
    time of this writing: float → int → ASCII-string). The first one that
    matches wins. This means that **The Perl scalar "123" will always be
    returned as an integer**


Quick Usage
-----------

::

    from storable import retrieve
    data = retrieve('/path/to/file.storable')

    from storable.output import serialize
    # only works (so far) for JSON-able types and recursion-limited depth
    # This will not serialize to the exact same object in perl as retrieve/thaw-ing
    # but will be readable by perl to load json-like values
    serialized_bytes = serialize({'x': 'bar', 'y': 1, 'z': 1.23, 'w':[], 'v':[1,2,3]})
