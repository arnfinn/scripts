#!/usr/bin/python
# Arnfinn Hykkerud Steindal, Tromso Oct. 2010
# Converts a xyz-file to a mol-file for Dalton
# TODO: 1) convert from au to angstrom, if needed
#       2) taking arguments
#       3) add more/all elements

import re
import sys
import shutil
import string
import os

basis = '6-31+G*'
# unit = angstrom

all   = [['C','',0,'6.0'],['N','',0,'7.0'],['O','',0,'8.0'],['S','',0,'16.0'],['H','',0,'1.0']]
arg   = sys.argv[1]
fact  = 7

a = len(arg)
xyz = open(arg,'r')
mol = open(arg[0:a-4]+'.mol','w')
filelen = a

lines = xyz.readlines()
a = len(lines)
xyz.seek(0)
for i in range(a):
    line = xyz.readline()
    words = line.split()
    for j in range(5):
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
for j in range(5):
    if all[j][2]>0:
        atmtps = atmtps + 1

# A test to see if we have an open shell system
test = 0.0
for j in range(5):
    test = test + float(all[j][2])*float(all[j][3])
print test
test = str(test/2.0)
test = test.split('.')
odd = False
if int(test[1])==5:
    print 'Odd number of electrons in file '+arg+'. Setting charge=-1 in '+arg[0:filelen-4]+'.mol'
    odd = True
mol.write('ATOMBASIS\n\
Structure from file '+arg+'\n\
----------------------\n\
AtomTypes='+str(atmtps)+' NoSymmetry Angstrom')
if odd:
    mol.write(' Charge=-1\n')
else:
    mol.write('\n')

for j in range(5):
    if all[j][2]>0:
        mol.write('        Charge='+all[j][3]+'   Atoms='+str(all[j][2])+'   \
Basis='+basis+'\n')
        mol.write(all[j][1])

mol.close()
xyz.close()
