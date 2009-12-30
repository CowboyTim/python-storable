#!/usr/bin/python

import storable
import sys

for f in sys.argv[1:]:
    print(storable.retrieve(f))
