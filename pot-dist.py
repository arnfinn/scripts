#!/usr/bin/env python
# Arnfinn Hykkerud Steindal, Tromso Oct 2013
# A script for finding the distance between 
# QM and a given MM site

import math
from argparse import ArgumentParser
import sys

def mol2xyz(mollines):
    xyz = []
    if mollines[0].split()[0] == "BASIS":
        k = 5
    elif mollines[0].split()[0] == "ATOMBASIS":
        k = 4
    for i in mollines[k:]:
        words = i.split()
        if words[0] in ["C","O","N","H"]:
            xyz.append(i)
    return xyz

def get_coord(potstring):
    words = potstring.split()
    x = float(words[1])
    y = float(words[2])
    z = float(words[3])
    return [x,y,z]

def get_distance(point1, point2):
    return math.sqrt(sum([(point1[i]-point2[i])**2 for i in range(3)]))

def get_dist(potcoord,molcoord,site):
    k = 0
    for i in potcoord:
        k += 1
        distlist = []
        if k == site:
            for j in molcoord:
                distlist.append(get_distance(i,j))
            return sorted(distlist)[0]
        
parser = ArgumentParser(description="My potential distance script")

parser.add_argument("-p", "--pot",dest="potfile",required=True, 
                    help="The pot input file")
parser.add_argument("-m", "--mol",dest="molfile",required=True,
                    help="The mol input file")
parser.add_argument("-s", "--site",type=int, dest="site",required=True,
                    help="The MM site for distance calculation")
args = parser.parse_args()

pot = open(args.potfile,"r")
potlines = pot.readlines()
pot.close()

mol = open(args.molfile,"r")
mollines = mol.readlines()
mol.close()

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

totnum = int(potlines[lcoor + 1])
if potlines[lcoor+2].split()[0] == "AA":
    ang = True
elif potlines[lcoor+2].split()[0] == "AU":
    ang = False
    quit("Script not yet implemented for atomic units")
else:
    quit("Something wrong. AU or AA in potfile not found where expected")

potcoord = []
for i in potlines[lcoor+3:lmul]:
    potcoord.append(get_coord(i))

xyzmol = mol2xyz(mollines)

molcoord = []
for i in xyzmol:
    molcoord.append(get_coord(i))

print "The distance between site {0} and the QM region is {1} angstrom.".format(args.site,get_dist(potcoord,molcoord,args.site))

