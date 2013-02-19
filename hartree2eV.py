#!/usr/bin/python
# Convert from hartree to eV (to nm)

import sys
print "The energy " + sys.argv[1] + " hartree corresponds to " + "%.4f" % (27.21138386*float(sys.argv[1])) + " eV and "+ "%.4f" % (1240.0/(27.21138386*float(sys.argv[1]))) + " nm."
