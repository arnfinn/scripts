#!/usr/bin/env python
# Arnfinn Hykkerud Steindal Oct 2014
# Script for running nPA calculations
# with openRSP

from argparse import ArgumentParser
import sys
import time

parser = ArgumentParser(description="nPA-openrsp run script")

parser.add_argument("-m", "--mol",dest="molfile", required=True,
                    help="The mol input file")
parser.add_argument("-p", "--pot",dest="potfile",
                    help="The pot input file (if peqm)")
parser.add_argument("-b", "--basis", dest="basis", default="d-aug-cc-pVDZ"
					help="The basis set [default: %(default)s]")
parser.add_argument("-f","--xc",dest="xc", default="CAMB3LYP"
					help="The XC functional [default: %(default)s]")

