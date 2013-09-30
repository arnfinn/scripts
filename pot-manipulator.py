#!/usr/bin/env python
# Arnfinn Hykkerud Steindal, Tromso Oct 2013
# A script for pot-file manipulation
# (removing alphas far from QM region)

import math
from argparse import ArgumentParser
import sys

def mol2xyz(mollines):
    xyz = []
    if mollines[0].split()[0] == "BASIS":
        for i in mollines[5:]:
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

def get_removallist(potcoord,molcoord,thr):
    k = 0
    rmlist = []
    for i in potcoord:
        k += 1
        distlist = []
        for j in molcoord:
            distlist.append(get_distance(i,j))
        if sorted(distlist)[0] > thr:
            rmlist.append(k)
    print len(rmlist)
    return rmlist
        
parser = ArgumentParser(description="My potential file manipulation script")

parser.add_argument("-p", "--pot",dest="potfile", 
                    help="The pdb input file")
parser.add_argument("--mol",dest="molfile",
                    help="The mol input file")
parser.add_argument("-t", "--threshold",type=float, dest="thr", default=5.0,
                    help="The threshold distance for removal of alphas")
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
    if words[0]=="EXCLIST":
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

xyz = mol2xyz(mollines)
molcoord = []
for i in xyz:
    molcoord.append(get_coord(i))

rmlist = get_removallist(potcoord,molcoord,args.thr)

newpot = ""
for i in potlines[0:lcoor]:
    newpot += i
newpot += "! "+str(len(rmlist))+" alphas removed by arnfinn\n"

for i in potlines[lcoor:lpol+2]:
    newpot += i

k = 0
for i in potlines[lpol+3:excl]:
    words = i.split()
    if int(words[0]) not in rmlist:
        k += 1
print k
newpot += str(k)+"\n"

print  str(int(potlines[lpol+2])-k)+"\n"

for i in potlines[lpol+3:excl]:
    words = i.split()
    if int(words[0]) not in rmlist:
        newpot += i

for i in potlines[excl:]:
    newpot += i

newpotfile = open("new.pot","w")
newpotfile.write(newpot)
newpotfile.close()
