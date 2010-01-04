#!/usr/bin/python

import storable
import sys
import pprint

p = pprint.PrettyPrinter(indent=4)
for f in sys.argv[1:]:
    p.pprint(storable.retrieve(f))
