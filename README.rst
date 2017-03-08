python-storable
===============

Overview
--------

This is a Python module that is be able to read Perl storable files. Storable
is a nice and efficient binary format for Perl that is very popular. A lot of
other serialization/deserialization modules exist that are even more or less
standardized: JSON, XML, CSV,.. etc. Storable is more or less Perl specific.

To ease integration between Perl - where storable sometimes is the only option
- and Python this module is a bridge.


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
