#!/usr/bin/env python

import os
import argparse as ap

def get_atomnum(ele):
    list={
        "H":1,
        "C":6,
        "N":7,
        "O":8
        }
    try:
        return list[ele]
    except:
        print "Element "+ele+" not in list. Please add it!"

numfiles=len(sys.arg[1:])
print numfiles
