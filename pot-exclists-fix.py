#!/usr/bin/env python
# Arnfinn Hykkerud Steindal, Tromso Oct 2013
# A script for pot-file manipulation
# (removing alphas far from QM region)

import math
from argparse import ArgumentParser
import sys
import time

def mol2xyz(mollines):
    xyz = []
    if mollines[0].split()[0] == "BASIS":
        k = 5
    elif mollines[0].split()[0] == "ATOMBASIS":
        k = 4
    for i in mollines[k:]:
        words = i.split()
        try:
            if words[0] in ["C","O","N","H"]:
                xyz.append(i)
        except:
            pass
    return xyz

def get_coord(potstring):
    words = potstring.split()
    x = float(words[1])
    y = float(words[2])
    z = float(words[3])
    return [x,y,z]

def get_distance(point1, point2):
    return math.sqrt(sum([(point1[i]-point2[i])**2 for i in range(3)]))

def get_removallist(potcoord,molcoord,thr,atoms):
    # atoms = number of atoms per solvent
    k = 0
    l = 0
    rmpol = []
    tmplist = []
    for i in potcoord:
        k += 1
        l += 1
        distlist = []
        for j in molcoord:
            distlist.append(get_distance(i,j))
        if sorted(distlist)[0] > thr:
            if atoms == 1:
                rmpol.append(k)
            else:
                tmplist.append(k)
        if atoms != 1:#water or hexane:
            if len(tmplist) == atoms:
                rmpol.extend(tmplist)
            if l == atoms:
                l = 0
                tmplist = []
    return rmpol


parser = ArgumentParser(description="My potential file manipulation script")

parser.add_argument("-p", "--pot",dest="potfile", required=True,
                    help="The pot input file")
parser.add_argument("-o", "--out",dest="outfile",default="tmp.pot",
                    help="The pot output file")
parser.add_argument("-w", "--water", action="store_true", dest="water", default=False, 
                    help="Water cluster (remove site only if all water sites are outside threshold)")
args = parser.parse_args()

pot = open(args.potfile,"r")
potlines = pot.readlines()
pot.close()

k=0
for i in potlines:
    words = i.split()
    if words[0]=="@COORDINATES":
        lcoor = k
    if words[0]=="@MULTIPOLES":
        lmul = k
    if words[0]=="@POLARIZABILITIES":
        lpol = k
    if words[0]=="EXCLISTS":
        excl = k
        break
    k += 1

num = []
l = 0
first = True
all_new = ""
for i in potlines[excl+2:]:
    k = 0
    try:
        a = i.split()[1]
    except:
        break
    num.append(int(i.split()[0]))
    for j in i.split():
        if int(j) != 0:
            k += 1
    if k == 3: # water molecule
        if first: # first water molecule. Start counting
            last_elem = num[-2]
            count = 0
            first = False
        count += 1
        l += 1
        if l == 1: # first water molecule
            new_exc = i.replace(i.split()[0],str(last_elem+count)).replace(i.split()[1],str(last_elem+count+1)).replace(i.split()[2],str(last_elem+count+2))
        elif l == 2:
            new_exc = i.replace(i.split()[0],str(last_elem+count)).replace(i.split()[1],str(last_elem+count-1)).replace(i.split()[2],str(last_elem+count+1))
        elif l == 3:
            new_exc = i.replace(i.split()[0],str(last_elem+count)).replace(i.split()[1],str(last_elem+count-2)).replace(i.split()[2],str(last_elem+count-1))
            l = 0
    else:
        new_exc = i

    all_new += new_exc

newpot = ""
for i in potlines[0:excl+2]:
    newpot += i
newpot +=all_new

newpotfile = open(args.outfile,"w")
newpotfile.write(newpot)
newpotfile.close()
