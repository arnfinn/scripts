#!/usr/bin/env python
# Arnfinn Hykkerud Steindal, Tromso Oct. 2010
# Converts a xyz-file to a mol-file for Dalton
# TODO: 1) convert from au to angstrom, if needed
#       3) add more/all elements

import re
import sys
import shutil
import string
import os

#from optparse import OptionParser
import argparse as ap


parser = ap.ArgumentParser()
parser.add_argument("-i", "--input",dest="filename", help="the file to read")
parser.add_argument("-b", "--basis",dest="basisset", default='aug-cc-pVDZ', help='''the basisset. [default: %(default)s]''')
parser.add_argument("-q", "--charge",dest="charge", help='''the molecular charge, +, - or 0''')

args = parser.parse_args()

filename=args.filename
basis = args.basisset
charge=args.charge
if charge:
    if charge not in ["0","+","-"]:
        print "WARNING: "+charge + " not a valid charge"

xyz = open(filename,'r')
a=len(filename)
mol=open(filename[0:a-4]+'.mol','w')

# unit = angstrom

all   = [['C','',0,'6.0'],['N','',0,'7.0'],['O','',0,'8.0'],['S','',0,'16.0'],['H','',0,'1.0']]
fact  = len(all)

filelen = a

lines = xyz.readlines()
a = len(lines)
xyz.seek(0)
for i in range(a):
    line = xyz.readline()
    words = line.split()
    for j in range(fact):
        try:
            atom=words[0][0]
            if atom== all[j][0]:
                newline=words[0]+fact*' '+words[1]+fact*' '+'\
'+words[2]+fact*' '+words[3]+'\n'
                all[j][1] = all[j][1] + newline
                all[j][2] = all[j][2] + 1
        except:
            break

atmtps = 0
for j in range(fact):
    if all[j][2]>0:
        atmtps = atmtps + 1

# A test to see if we have a charged system
test = 0.0
test2 = 0
for j in range(fact):
    test = test + float(all[j][2])*float(all[j][3])
running=True
j=0

test = str(test/2.0)
test = test.split('.')
odd = False
if int(test[1])==5 and not charge in ["+","-","0"]:
    answer=True
    print "The molecule in file "+filename+" has a odd number of protons."
    charge = raw_input("Is it neutral (0), positively (+), or negatively (-) charged? ")
    while answer:
        if charge in ["+","-","0"]:
            answer = False
        else:
            print "The answer "+str(charge)+" not valid!"
            charge = raw_input("Please press 0 for neutral (open shell), + for positively  or - for negatively charged molecule: ")

mol.write('BASIS\n\
'+basis+'\n\
Structure from file '+filename+'\n\
using my xyz2mol.py 0.1.1 \n\
AtomTypes='+str(atmtps)+' NoSymmetry Angstrom')
if charge=="+":
    mol.write(' Charge=1\n')
elif charge=="-":
    mol.write(' Charge=-1\n')
else:
    mol.write('\n')

for j in range(fact):
    if all[j][2]>0:
        mol.write('        Charge='+all[j][3]+'   Atoms='+str(all[j][2])+'\n')
        mol.write(all[j][1])

mol.close()
xyz.close()
