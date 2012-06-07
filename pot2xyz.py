#!/usr/bin/python
# Arnfinn Hykkerud Steindal, Tromso Dec 2010
# Converts a dalton pot-file to a xyz-file

import re
import sys
import shutil
import string
import os

def au2ang(num):
    return float(num)/1.889725989

atmnr = ['1','6','7','8','16']
atmnm = ['H','C','N','O','S']

for arg in sys.argv[1:]:
    cntr = 0
    inpxyz = ''
    pot = open(arg+'.pot','r')
    lines = pot.readlines()
    pot.close()
    words = lines[0].split()
    if words[0] == 'AU':
        au = True
    else:
        au = False
    words = lines[1].split()
    a = int(words[3])
    b = int(words[0])
    xyz = open(arg+'.xyz','w')
    xyz.write(str(b)+'\n\n')
    tall = 0
    for i in lines[2:]:
        tall = tall + 1
        words = i.split()
        d = 5
        if au:
            x = str(au2ang(words[a+1]))
            y = str(au2ang(words[a+2]))
            z = str(au2ang(words[a+3]))
        else:
            x = words[a+1]
            y = words[a+2]
            z = words[a+3]
        for j in range(len(atmnr)):
            if words[a] == atmnr[j]:
                first = atmnm[j]
        xyz.write(first+str(tall) + d*' '+x+d*' '+y+d*' '+z+'\n')
    xyz.close()
