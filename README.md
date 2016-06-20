# python-storable3

This is a port of the original [python-storable](https://github.com/CowboyTim/python-storable) module to Python 3, with some enhancements.

python-storable is a python module that can read/write perl storable files. 
Storable is a nice and efficient binary format for perl that is very popular, 
though it is more or less perl specific.

This module is a bridge to ease integration between perl, where storable sometimes is the only option.

## Progress

This module is beta quality, though I use it in production as-is. It has 
limited support for writing, being able to handle:

* lists
* dicts
* strings (only if they can be encoded as utf8)
* integers
* floats

Though if you pass it any other object, it will call str() on it, so it is
fairly safe and shouldn't crash.

I have no plans to attempt to add the ability to read or write classes or
any other advanced data type. That is madness.

## Authors
* [CowboyTim](https://github.com/CowboyTim)
* [Quasarj](https://github.com/Quasarj)
* And anyone else that is in the commit history :)

### License
zlib/libpng. See LICENSE.txt for details.

