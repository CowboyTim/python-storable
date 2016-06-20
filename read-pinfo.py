import sys
import pprint

import storable

filename = sys.argv[1]

data = storable.retrieve(filename)

pprint.pprint(data)
