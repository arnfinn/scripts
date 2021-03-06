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
    def __init__(self, num, o, h1, h2, dist=0.0, com=[0.0,0.0,0.0]):
        self.num = num
        self.o = o
        self.h1 = h1
        self.h2 = h2
        self.dist = dist
        self.com = com
    def __repr__(self):
        return repr((self.num, self.o, self.h1, self.h2, self.dist, self.com))

def get_PBC(lines):
    # periodic boundary conditions
    try:
        for i in lines[0:10]:
            k = i.split()
            if k[0] == "CRYST1":
                coord = [float(k[1]), float(k[2]), float(k[3])]
    except:
        return False
    return coord

def get_com(mol):
    label_2_mass = {'H':1.0079, 'Li':6.9400, 'Be':9.0122, 'B':10.8100,
                    'C':12.0110, 'N':14.0067, 'O':15.9994, 'F':18.9984,
                    'Na':22.9898, 'Mg':24.3100, 'Al':26.9800, 'Si':28.0860,
                    'P':30.9740, 'S':32.0600, 'Cl':35.4530, 'Br':79.9040}
    mx, my, mz, M = 0.0, 0.0, 0.0, 0.0
    for atoms in mol:
        mx += label_2_mass[atoms[0]]*atoms[1]
        my += label_2_mass[atoms[0]]*atoms[2]
        mz += label_2_mass[atoms[0]]*atoms[3]
        M += label_2_mass[atoms[0]]
    return [mx/M,my/M,mz/M]

def get_coord(pdbstring):
    x = float(pdbstring[30:38])
    y = float(pdbstring[38:46])
    z = float(pdbstring[46:54])
    return [x,y,z]

def get_distance(point1, point2):
    return math.sqrt(sum([(point1[i]-point2[i])**2 for i in range(3)]))

def get_2D_distance(point1, point2):
    return math.sqrt(sum([(point1[i]-point2[i])**2 for i in range(2)]))

def get_angle(point1, point2, point3, rad=False):
    """
    Get the angle between three points
    """
    vec1 = geometry.create_vector([point1[i] - point2[i] for i in range(3)])
    vec2 = geometry.create_vector([point3[i] - point2[i] for i in range(3)])
    if rad:
        return geometry.angle(vec1, vec2)
    else:
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

def get_mylist(lines,point=None):
    mylist = []
    for i in lines:
        ele = i[13:16]
        o = ["OW ","O  "]
        h1 = ["HW1","H1 "]
        h2 = ["HW2","H2 "]
        if ele in o:
            n = int(i[21:26])
            a = get_coord(i)
            if point:
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
#            com = get_com([])
            mylist.append(H2O(n,a,b,c,dist))
    return mylist

def get_point(lines, num=5, thr=0.5, surface=True):
    mylist = get_mylist(lines)
    # x
    a = sorted(mylist, key=lambda c: c.o[0])
    xmin, xmax = a[0].o[0], a[-1].o[0]
    x, xlen = (xmin+xmax)/2, xmax - xmin
    # y
    a = sorted(mylist, key=lambda c: c.o[1])
    ymin, ymax = a[0].o[1], a[-1].o[1]
    y, ylen = (ymin+ymax)/2, ymax - ymin
    # z
    a = sorted(mylist, key=lambda c: c.o[2])
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
    else:
        for i in a[0:num]:
            myz.append(i.o[2])
    newz = list(myz)
    aver = sum(i for i in myz)/len(myz)
    #check for outliers in the z-direction
    for i in range(len(myz)):
        if abs(myz[i]-aver)>thr:
            newz.pop(0)
            aver = sum(k for k in newz)/len(newz)
    if surface:
        # z is at the first water molecule, minus some
        z = newz[0]-0.01
    else:
        a = sorted(mylist, key=lambda c: c.o[2], reverse=True)
        zmin = newz[0]
        myz = []
        for i in a[0:num]:
            myz.append(i.o[2])
        newz = list(myz)
        aver = sum(i for i in myz)/len(myz)
        for i in range(len(myz)):
            if abs(myz[i]-aver)>thr:
                newz.pop(0)
                aver = sum(k for k in newz)/len(newz)
        zmax = newz[0]
        z = (zmin+zmax)/2
    return [x,y,z]


def arg_checker(args):
    if args.filename[-4:]!= ".pdb":
        exit('I only eat pdb files, not {0} files!'.format(args.filename[-3:]))
    if file:
        try:
            finp = open(args.filename,"r")
        except:
            exit('Can not open file {0}. Does it exist?'.format(args.filename))
        finp.close()
    else:
        exit('You have to specify an input file! (-i <filename>)')
    if args.thr and args.numbers:
        print "Warning! -n "+str(args.numbers)+" has also been specified.\n\
Threshold will only be used if one of the "+str(args.numbers)+" closest\n\
water molecules are closer than "+str(args.thr) + " angstrom from \n\
the point."


parser = ArgumentParser(description="My water cluster pdb manipulation script")

parser.add_argument("-i", "--input",dest="filename", 
                    help="The pdb input file")
parser.add_argument("--xyz", action="store_true", dest="xyz", default=False, 
                    help="Make one xyz-file of a set of water molecules")
parser.add_argument("-d","--dalton", action="store_true", dest="dalton", default=False, 
                    help="Make dalton mol file of some water molecules")
parser.add_argument("--pdb", action="store_true", dest="pdb", default=False, 
                    help="Make pdb file of the remaining water molecules")
parser.add_argument("--geom", action="store_true", dest="geom", default=False, 
                    help="Print geometrical parameters")
parser.add_argument("-v", "--verbose", action="store_true", dest="verbose", default=False, 
                    help="More printing")
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
                    help="Detect a good point at the surface")
parser.add_argument("--middle", action="store_true", dest="middle", default=False, 
                    help="Detect the point in the middle of the bulk")

args = parser.parse_args()

arg_checker(args)

#if args.verbose:
#    arglist = str(args)[10:-1].split()
#    text= "The following arguments are used:\n"
#    for i in arglist:
#        text += i + " "
#    print text

file = args.filename
finp = open(file,"r")
lines = finp.readlines()
finp.close()

point = None

if args.point:
    point = [float(j) for j in args.point]

# try to detect a good starting point in the middle of a bulk
if args.middle:
    point = get_point(lines, surface=False)

# try to detect a good starting point at the surface,
# in the beginning of z and in the middle of x-y
if args.surface:
    point = get_point(lines, surface=True)

if not point:
    if args.thr:
        print "WARNING! You have specified a threshold (-t), but no point.\n\
Setting point to 0.0, 0.0, 0.0"
        point = [0.0,0.0,0.0]
    elif args.numbers:
        print "WARNING! You have specified a number (-n NUM), but no point.\n\
Setting point to 0.0, 0.0, 0.0"
        point = [0.0,0.0,0.0]

# put all the water molecules in "mylist"
mylist = get_mylist(lines,point)

# sort the mylist according to the distance from "args.point"
h2o_list = []
if point:
    a =  sorted(mylist, key=lambda cluster: cluster.dist) 
    k = 1
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
    h2o_list = [i.num for i in a[0:k]]
    waters = k

if args.pdb:
    new_pdb=""
    for i in lines:
        if i[0:4]=="ATOM":
            n = int(i[21:26])        
            if n not in h2o_list:
                new_pdb+=i
    filename = file.split(".")[0]+"-new.pdb"
    filewriter(filename,new_pdb)

#    left1 = org_clus(a[waters:],"O")
#    left2 = org_clus(a[waters:],"H")


if args.dalton:
    arglist = str(args)[10:-1].split()
    newarg = list(arglist)
    # remove thing I do not care about
    notincl = ["None", "False", "basis=", "filename=", "dalton=", "all=", "xyz=", "pdb=", "verbose=", "geom="]
    for i in arglist:
        for k in notincl:
            if k in i:
                newarg.remove(i)
                break
    text = "ATOMBASIS\nStructure from {0} with the settings\n".format(args.filename)
    for i in newarg:
        text += i + " "
    text += "coord: "
    text +=" ".join(str(i) for i in point)
    text += "\nAtomTypes=2 NoSymmetry Angstrom\n"
    text += "Charge=8.0  Atoms={0}   Basis={1}\n".format(waters,args.basis)
    text += oxygen
    text += "Charge=1.0  Atoms={0}   Basis={1}\n".format(2*waters,args.basis)
    text += hydrogen
    filename = file.split(".")[0]+".mol"
    filewriter(filename,text)
    if args.verbose:
        print text

if args.xyz:
    text = str(3*waters)+"\n\n"
    text += oxygen
    text += hydrogen
    filename = file.split(".")[0]+".xyz"
    filewriter(filename,text)

# make xyz files of all the water molecules
if args.all:
    for i in mylist:
        filename = file.split(".")[0]+"-"+str(i.num)+".xyz"
        text = "3\n\n"+clus2xyz(i,"O")+clus2xyz(i,"H")
        filewriter(filename,text)



#Some testing of structures
if args.geom:
    for i in mylist:
        print "dist/angle \
" + str("%.3f" % get_distance(i.o,i.h1)) + " \
" + str("%.3f" % get_distance(i.o,i.h2)) + " \
" + str("%.1f" % get_angle(i.h1,i.o,i.h2))

a = ["O",1.0,1.0,1.0]
b = ["H",1.0,2.0,1.0]
c = ["H",1.0,1.0,2.0]
print get_com([a,b,c])
