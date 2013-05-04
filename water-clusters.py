#!/usr/bin/env python
# Arnfinn Hykkerud Steindal, Tromso 2013
# A script for manipulating pdb-files with
# water clusters

import math
#from optparse import OptionParser
from argparse import ArgumentParser
import sys
import geometry
from numpy import pi

class H2O:
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

def get_2D_distance(point1, point2):
    return math.sqrt(sum([(point1[i]-point2[i])**2 for i in range(2)]))

def get_angle(point1, point2, point3):
    """
    Get the angle between three points
    """
    vec1 = geometry.create_vector([point1[i] - point2[i] for i in range(3)])
    vec2 = geometry.create_vector([point3[i] - point2[i] for i in range(3)])
    return 360*geometry.angle(vec1, vec2)/(2*pi)

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

def get_point(mylist, num=5, thr=0.5, surface=True):
    # x
    a = sorted(mylist, key=lambda cluster: cluster.o[0])
    xmin, xmax = a[0].o[0], a[-1].o[0]
    x, xlen = (xmin+xmax)/2, xmax - xmin
    # y
    a = sorted(mylist, key=lambda cluster: cluster.o[1])
    ymin, ymax = a[0].o[1], a[-1].o[1]
    y, ylen = (ymin+ymax)/2, ymax - ymin
    # z
    a = sorted(mylist, key=lambda cluster: cluster.o[2])
    myz = []
    k = 0
    if surface:
        dist = min(xlen,ylen)/4
        for i in a:
            # only take into consideration water molecules in the middle
            # of the x-y plane
            if get_2D_distance([i.o[0],i.o[1]],[x,y])<dist:
                k += 1
                myz.append(i.o[2])
                if k > num:
                    break
        newz = list(myz)
        aver = sum(i for i in myz)/len(myz)
    else:
        for i in a[0:num]:
            myz.append(i.o[2])
    #check for outliers in the z-direction
    for i in range(len(myz)):
        if abs(myz[i]-aver)>thr:
            newz.pop(0)
            aver = sum(k for k in newz)/len(newz)
    if surface:
        # z is at the first water molecule, minus some
        z = newz[0]-0.01
    else:
        zmin = newz[0]
        myz = []
        for i in a[-num:-1]:
            myz.append(i.o[2])
            

        

    z = (a[0].o[2]+a[-1].o[2])/2
    return [x,y,z]

def get_surface_point(mylist, num=5, thr=0.5):
    # x
    a = sorted(mylist, key=lambda cluster: cluster.o[0])
    xmin, xmax = a[0].o[0], a[-1].o[0]
    x, xlen = (xmin+xmax)/2, xmax - xmin
    # y
    a = sorted(mylist, key=lambda cluster: cluster.o[1])
    ymin, ymax = a[0].o[1], a[-1].o[1]
    y, ylen = (ymin+ymax)/2, ymax - ymin
    # z
    a = sorted(mylist, key=lambda cluster: cluster.o[2])
    myz = []
    k = 0
    dist = min(xlen,ylen)/4
    for i in a:
        # only take into consideration water molecules in the middle
        # of the x-y plane
        if get_2D_distance([i.o[0],i.o[1]],[x,y])<dist:
            k += 1
            myz.append(i.o[2])
            if k > num:
                break
    newz = list(myz)
    aver = sum(i for i in myz)/len(myz)
    #check for outliers in the z-direction
    for i in range(len(myz)):
        if abs(myz[i]-aver)>thr:
            newz.pop(0)
            aver = sum(k for k in newz)/len(newz)
    # z is at the first water molecule, minus some
    z = newz[0]-0.001
    return [x,y,z]

parser = ArgumentParser(description="My water cluster pdb manipulation script")
parser.add_argument("-i", "--input",dest="filename", 
                    help="The pdb input file")
parser.add_argument("--xyz", action="store_true", dest="xyz", default=False, 
                    help="Make one xyz-file of a set of water molecules")
parser.add_argument("-d","--dalton", action="store_true", dest="dalton", default=False, 
                    help="Make dalton mol file of some water molecules")
parser.add_argument("-a","--all", action="store_true", dest="all", default=False, 
                    help="Make xyz-files of all the water molecules")
parser.add_argument("-p", "--point",type=float, dest="point", nargs=3, 
                    help="The origin (x, y, z) from where to extract water molecules")
parser.add_argument("-t", "--threshold",type=float, dest="thr", 
                    help="The threshold distance for removal of water molecules (sphere)")
parser.add_argument("-n","--num",type=int, dest="numbers", 
                    help="Numbers of water molecules to be extracted")
parser.add_argument("-b", "--basis",dest="basis", default="6-31+G*",
                    help="The basis set, for dalton input")
parser.add_argument("--cyllinder",type=float, dest="cyllinder", nargs=2, 
                    help="Keep all water molecules inside a cyllinder with given radius and height.")
parser.add_argument("--cuboid",type=float, dest="cuboid", nargs=3, 
                    help="Keep all water molecules inside a cuboid of given size (x, y, z)")
parser.add_argument("--surface", action="store_true", dest="surface", default=False, 
                    help="Detect a good point (at the z-surface)")
parser.add_argument("--middle", action="store_true", dest="middle", default=False, 
                    help="Detect the point in the middle of the bulk")


args = parser.parse_args()

file = args.filename
if file:
    try:
        finp = open(file,"r")
    except:
        exit('Can not open file {0}. Does it exist?'.format(file))
else:
    exit('You have to specify an input file! (-i <filename>)')

#if not args.numbers and not args.thr and not args.point and not args.all:
#    exit("Please specify something to do with your input file!")

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

#if args.thr and args.numbers:
#    print "Warning! -n "+str(numb)+" has also been specified.\n\
#Threshold will only be used if one of the "+str(numb)+" closest\n\
#water molecules are closer than "+str(args.thr) + " angstrom from \n\
#the point "+" ".join(str(i) for i in args.point)

#if args.point and (not args.thr and not args.numbers):
#    quit("You have specified a point, but please specify what you want to do.\n\
#You can either use -n <number> or -t <threshold>")

lines = finp.readlines()
finp.close()

# put all the water molecules in "mylist"
mylist = []
for i in lines:
    ele = i[13:16]
    o = ["OW ","O  "]
    h1 = ["HW1","H1 "]
    h2 = ["HW2","H2 "]
    if ele in o:
        n = int(i[21:26])
        a = get_coord(i)
        if args.point or args.numbers or args.thr:
            dist = get_distance(a,point)
        else:
            dist = 0.0
    elif ele in h1:
        if n != int(i[21:26]):
            exit("wrong1")
        b = get_coord(i)
    elif ele in h2:
        if n != int(i[21:26]):
            exit("wrong2")
        c = get_coord(i)
        mylist.append(H2O(n,a,b,c,dist))

test=True
if test:
    for i in mylist:
        print "dist/angle \
" + str("%.3f" % get_distance(i.o,i.h1)) + " \
" + str("%.3f" % get_distance(i.o,i.h2)) + " \
" + str("%.1f" % get_angle(i.h1,i.o,i.h2))

# make xyz files of all the water molecules
if args.all:
    for i in mylist:
        filename = file.split(".")[0]+"-"+str(i.num)+".xyz"
        text = "3\n\n"+clus2xyz(i,"O")+clus2xyz(i,"H")
        filewriter(filename,text)

# try to detect a good starting point in the middle of a bulk
if args.middle:
    point = get_middle_point(mylist)

# try to detect a good starting point at the surface,
# in the beginning of z and in the middle of x-y
if args.surface:
    point = get_surface_point(mylist)
    if args.cyllinder:
        point = [point[0],point[1],(point[2]+args.cyllinder[1]/2)]
    print point

# sort the mylist according to the distance from "args.point"
if args.point or args.thr or args.numbers:
    a =  sorted(mylist, key=lambda cluster: cluster.dist) 
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

