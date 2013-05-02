#!/usr/bin/env python
# Arnfinn Hykkerud Steindal, Tromso 2013
# A script for manipulating pdb-files with
# water clusters

import math
#from optparse import OptionParser
from argparse import ArgumentParser
import sys

class Cluster:
    def __init__(self, num, o, h1, h2, dist=0.0):
        self.num = num
        self.o = o
        self.h1 = h1
        self.h2 = h2
        self.dist = dist
    def __repr__(self):
        return repr((self.num, self.o, self.h1, self.h2, self.dist))


def get_coord(pdbstring):
    x = float(pdbstring[30:38])
    y = float(pdbstring[38:46])
    z = float(pdbstring[46:54])
    return [x,y,z]

def get_distance(point1, point2):
    return math.sqrt(sum([(point1[i]-point2[i])**2 for i in range(3)]))

def clus2xyz(clus,ele):
    space = 8
    string = ""
    if ele is "O":
        coord = [clus.o]
    elif ele is "H":
        coord = [clus.h1,clus.h2]
    for i in coord:
        string += ele
        for j in i:
            a = space-len(str(j).split(".")[0])
            string += a*" " + str("%.6f" % j)
        string += "\n"
    return string

def org_clus(clus,ele):
    string = ""
    for i in clus:
        string += clus2xyz(i,ele)
    return string

def filewriter(filename,text):
    file = open(filename,"w")
    file.write(text)
    file.close()

parser = ArgumentParser(description="My water cluster pdb manipulation script")
parser.add_argument("-i", "--input",dest="filename", 
                    help="The pdb input file")
parser.add_argument("--xyz", action="store_true", dest="xyz", default=False, 
                    help="Make xyz-files of water molecules")
parser.add_argument("-d","--dalton", action="store_true", dest="dalton", default=False, 
                    help="Make dalton mol file of some water molecules")
parser.add_argument("-a","--all", action="store_true", dest="all", default=False, 
                    help="Make xyz-files of all the water molecules")
parser.add_argument("-p", "--point",type=float, dest="point", nargs=3, 
                    help="The origin (x, y, z) from where to extract water molecules")
parser.add_argument("-t", "--threshold",type=float, dest="thr", 
                    help="The threshold distance for removal of water molecules")
parser.add_argument("-n","--num",type=int, dest="numbers", 
                    help="Numbers of water molecules to be extracted")
parser.add_argument("-b", "--basis",dest="basis", default="6-31+G*",
                    help="The basis set, for dalton input")

args = parser.parse_args()

file = args.filename
if file:
    try:
        finp = open(file,"r")
    except:
        exit('Can not open file {0}. Does it exist?'.format(file))
else:
    exit('You have to specify an input file! (-i <filename>)')

if not args.numbers and not args.thr and not args.point and not args.all:
    exit("Please specify something to do with your input file!")

if args.numbers:
    numb = int(args.numbers)
if args.point:
    point = [float(j) for j in args.point]
elif args.thr:
    print "WARNING! You have specified a threshold (-t), but no point (-p).\n\
Setting point to 0.0, 0.0, 0.0"
    point = [0.0,0.0,0.0]
elif args.numbers:
    print "WARNING! You have specified a number (-n NUM), but no point (-p x y z).\n\
Setting point to 0.0, 0.0, 0.0"
    point = [0.0,0.0,0.0]

if args.thr and args.numbers:
    print "Warning! -n "+str(numb)+" has also been specified.\n\
Threshold will only be used if one of the "+str(numb)+" closest\n\
water molecules are closer than "+str(args.thr) + " angstrom from \n\
the point "+" ".join(str(i) for i in args.point)

if args.point and (not args.thr and not args.numbers):
    quit("You have specified a point, but please specify what you want to do.\n\
You can either use -n <number> or -t <threshold>")

lines = finp.readlines()
finp.close()

# put all the water molecules in "list"
list = []
for i in lines[2:]:
    if i[13:16]=="OW ":
        n = int(i[21:26])
        a = get_coord(i)
        if args.point or args.numbers or args.thr:
            dist = get_distance(a,point)
        else:
            dist = 0.0
    elif i[13:16]=="HW1":
        if n != int(i[21:26]):
            exit("wrong1")
        b = get_coord(i)
    elif i[13:16]=="HW2":
        if n != int(i[21:26]):
            exit("wrong2")
        c = get_coord(i)
        list.append(Cluster(n,a,b,c,dist))

# make xyz files of all the water molecules
if args.all:
    for i in list:
        filename = file.split(".")[0]+"-"+str(i.num)+".xyz"
        text = "3\n\n"+clus2xyz(i,"O")+clus2xyz(i,"H")
        filewriter(filename,text)
        
# sort the list according to the distance from "args.point"
if args.point or args.thr or args.numbers:
    a =  sorted(list, key=lambda cluster: cluster.dist) 
    k = 0
    if args.thr:
        for i in a:
            k += 1
            if args.numbers:
                if k>=args.numbers:
                    break
            if i.dist > args.thr:
                break
    elif args.numbers:
        k = args.numbers
    oxygen = org_clus(a[0:k],"O")
    hydrogen = org_clus(a[0:k],"H")
    print a[0:k]
    waters = k
#    print k
#    print org_clus(a[0:k],"O")

if args.dalton:
    text = "ATOMBASIS\nStructure from {0} with the settings\n".format(args.filename)
    text += "coord: "
    text +=" ".join(str(i) for i in point)
    if args.numbers:
        text +=", n={0}".format(args.numbers)
    if args.thr:
        text +=", thr={0}".format(args.thr)
    text += "\nAtomTypes=2 NoSymmetry Angstrom\n"
    text += "Charge=8.0  Atoms={0}   Basis={1}\n".format(waters,args.basis)
    text += oxygen
    text += "Charge=1.0  Atoms={0}   Basis={1}\n".format(2*waters,args.basis)
    text += hydrogen
    filename = file.split(".")[0]+".mol"
    filewriter(filename,text)

if args.xyz:
    text = str(3*waters)+"\n\n"
    text += oxygen
    text += hydrogen
    filename = file.split(".")[0]+".xyz"
    filewriter(filename,text)

