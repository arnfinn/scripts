#!/usr/bin/python
# Convert from eV to nm

import sys
print "The energy " + sys.argv[1] + " eV corresponds to " + "%.2f" % (1240.0/float(sys.argv[1])) + " nm."
