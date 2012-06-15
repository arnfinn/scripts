#!/usr/bin/python
# Arnfinn Hykkerud Steindal, Tromso July 2011
# Get the largest PE induced dipoles from an output file.

import re
import sys
import shutil
import string
import math

for i in sys.argv[1:]:
    try:
        file = open(i,'r')
    except:
        print 'Did not find file '+i
        break
    start = False
    lines = file.readlines()
    k = 0
    dipoles=[]
    cont=True
    for line in lines:
        if False:
    #        if '' in lines:
            l=0
            while (cont):
                l=l+1
                try:
                    a=int(line(k+l+3).split()[0])
                except:
                    cont=False
        if 'Final results from SIRIUS' in line:
            fac=65
            start = True
        if 'FINAL RESULTS FROM SIRIUS' in line:
            fac=56
            start = True
        if start:
            try:
                num= int(lines[k-fac].split()[0])
            except:
                try:
                    fac = fac + 2
                    num= int(lines[k-fac].split()[0])
                except:
                    print 'Something wrong with line'
                    print lines[k-fac]
                    break
            for j in range(num):
                dipoles.append([])
                site=lines[k-num-fac+j+1].split()
                x2=float(site[1])*float(site[1])
                y2=float(site[2])*float(site[2])
                z2=float(site[3])*float(site[3])
                dipoles[j].append(math.sqrt(x2+y2+z2))
                dipoles[j].append(j+1)
#                test = sorted(dipoles, key=lambda dip: dip[1])
                dipoles.sort(reverse=True)
            break
        k = k + 1
    print 'The ten highest induced dipole moments:'
    for j in range(10):
        site=str(dipoles[j][1])
        a=7-len(site)
        print site + a*' ' +  str(dipoles[j][0])
    file.close()
