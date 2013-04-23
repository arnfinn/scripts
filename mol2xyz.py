#!/usr/bin/python
# Arnfinn Hykkerud Steindal, Tromso May 2009
# Converts a dalton mol-file to a xyz-file
# TODO: 1) make it work with new input
#       2) convert from au to angstrom, if needed

import re
import sys
import shutil
import string
import os

for arg in sys.argv[1:]:
    cntr = 0
    tall = 0
    inpxyz = ''
    b=len(arg)
    mol = open(arg,'r')
    xyz = open(arg[0:b-4]+'.xyz','w')
    lines = mol.readlines()
    a = len(lines)
    mol.seek(0)
    line = mol.readline()
    if line[0:5] == 'BASIS':
        for i in range(4):
            line = mol.readline()
    else:
        for i in range(3):
            line = mol.readline()
    words = line.split()
    tst = words[0]
    if str.capitalize(tst[0:9])=='Atomtypes':
        moltps = int(tst[10:])
    else:
        moltps = int(words[0])
    for i in range(moltps):
        line = mol.readline()
        words = line.split()
        tst = words[1]
        if str.capitalize(tst[0:5])=='Atoms':
            atms = int(tst[6:])
        else:
            atms = int(words[1])
#        atms = int(words[1])
        for k in range(atms):
            line = mol.readline()
            words = line.split()
            if len(words[1])<14:
                a = 15 - len(words[1])
                b = 15 - len(words[2])
                c = 15 - len(words[3])
            else:
                a = 20 - len(words[1])
                b = 20 - len(words[2])
                c = 20 - len(words[3])
            cntr = cntr + 1
            # + str(cntr)
            tall = tall + 1
            inpxyz = inpxyz + words[0]+str(tall)+a*' '+words[1]+b*' ' + '\
'+ words[2] + c*' ' +  words[3] + '\n'
    xyz.write(str(cntr) + '\n\
' + '\n' + inpxyz)
    mol.close()
    xyz.close()
