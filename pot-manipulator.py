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
parser.add_argument("-m", "--mol",dest="molfile", required=True,
                    help="The mol input file")
parser.add_argument("-o", "--out",dest="outfile",default="tmp.pot",
                    help="The pot output file")
parser.add_argument("-t", "--thrpol",type=float, dest="thrpol", default=5.0,
                    help="The threshold distance for removal of alphas")
parser.add_argument("-t2", "--thrmul",type=float, dest="thrmul",
                    help="The threshold distance for removal of multipoles")
parser.add_argument("--xyz", action="store_true", dest="xyz", default=False, 
                    help="Make xyz-files of polarization sites (and multipoles if requested)")
parser.add_argument("-w", "--water", action="store_true", dest="water", default=False, 
                    help="Water cluster (remove site only if all water sites are outside threshold)")
parser.add_argument("--hexane", action="store_true", dest="hexane", default=False, 
                    help="Hexane cluster (remove site only if all hexane sites are outside threshold)")
parser.add_argument("-a", "--atoms",type=int, dest="atoms",
                    help="Number of atoms in the solvent molecule")
parser.add_argument("-s", "--solvent", dest="solvent",
                    help="Name of the solvent")
parser.add_argument("-v", action="store_true", dest="verbose", default=False, 
                    help="Print more")
first_time = time.time()

args = parser.parse_args()

xyz = args.xyz

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

# Check that number of coordinates equals 
# number of pol. and multipols
num_coord = int(potlines[lcoor+1])
num_mul   = int(potlines[lmul+2])
num_pol   = int(potlines[lpol+2])
if num_mul != num_coord or num_pol != num_coord:
    quit("Number of coordinates ({0}) not equal number of multipoles ({1}) and/or polarizabilities ({2}) (diff {3}).".format(num_coord,num_mul,num_pol,num_coord-num_mul))

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

if args.solvent:
    sol_dict = {
        "hexane":20,
        "water":3,
        "methanol":6,
        "tetra":5
        }
    try:
        numatom = sol_dict[args.solvent]
    except:
        quit("Solvent {0} not known".format(args.solvent))
elif args.atoms:
    numatom = args.atoms
elif args.water:
    numatom = 3
elif args.hexane:
    numatom = 20
else:
    numatom = 1

rmpol = set(get_removallist(potcoord,molcoord,args.thrpol,numatom))
polleft = int(potlines[lpol+2])-len(rmpol)

if args.thrmul:
    rmmul =  set(get_removallist(potcoord,molcoord,args.thrmul,numatom))
    mulleft = int(potlines[lcoor+1])-len(rmmul)

newpot = ""
for i in potlines[0:lcoor]:
    newpot += i
newpot += "! {0} alphas removed by arnfinn\n".format(str(len(rmpol)))
newpot += "! outside a threshold of {0} angstrom\n".format(args.thrpol)
if args.thrmul:
    newpot += "! {0} MM sites removed with threshold {1} AA.\n".format(str(len(rmmul)),args.thrmul)

newpot += potlines[lcoor]+potlines[lcoor+1]+potlines[lcoor+2]

for i in potlines[lcoor+3:lmul]:
    newpot += i

if args.thrmul:
    # remove multipoles...
    begin = False
    newpot += potlines[lmul]
    for i in potlines[lmul+1:lpol]:
        words = i.split()
        if words[0] == "ORDER":
            order = int(words[1])
            begin = True
            newpot += i
        elif begin:
            newpot += str(int(potlines[lcoor+1])-len(rmmul)) + "\n"
            begin = False
        elif int(words[0]) not in rmmul:
            newpot += i
    newpot += potlines[lpol] + potlines[lpol+1] 
else:
    for i in potlines[lmul:lpol+2]:
        newpot += i

newpot += "{0}\n".format(polleft)

for i in potlines[lpol+3:excl]:
    words = i.split()
    if int(words[0]) not in rmpol:
        newpot += i

for i in potlines[excl:]:
    newpot += i

newpotfile = open(args.outfile,"w")
newpotfile.write(newpot)
newpotfile.close()

if args.verbose:
    print "Number of polarizable sites left with threshold {0} are {1}".format(args.thrpol,polleft)
    if args.thrmul:
        print "Number of multipoles sites left with threshold {0} are {1}".format(args.thrmul,mulleft)
else:
    print "{0}    {1}".format(args.thrpol,polleft)

# Make xyz files
if xyz:
    k = 0
    xyzpot = ""
    xyzmul = ""
    for i in potlines[lcoor+3:lmul]:
        k += 1
        if k not in rmpol:
            xyzpot += i
        if args.thrmul:
            if k not in rmmul:
                xyzmul += i

    xyz2 = open("pot.xyz","w")
    xyz2.write("{0}\n".format(polleft)+xyzpot)
    xyz2.close()
    if args.thrmul:
        xyz2 = open("mul.xyz","w")
        xyz2.write("{0}\n".format(mulleft)+xyzmul)
        xyz2.close()



# A test:
k = 0
for i in potlines[lpol+3:excl]:
    words = i.split()
    if int(words[0]) not in rmpol:
        k += 1
if k != polleft:
    print "Something wrong! k ({0}) not equatl polleft ({1})".format(k,polleft)

if args.verbose:
    last_time = time.time()
    print "Seconds used: {0}".format(last_time - first_time)
