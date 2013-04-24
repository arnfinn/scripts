#!/usr/bin/env python


import sys
import re
import numpy as np
import math
from argparse import ArgumentParser

def norm(vector):
    """ Returns the norm (length) of the vector."""
    return np.sqrt(np.dot(vector, vector))

def unit_vector(vector):
    """ Returns the unit vector of the vector.  """
    return vector / norm(vector)

def angle_between(v1, v2):
    """ Returns the angle in radians between vectors 'v1' and 'v2' """
    v1_u = unit_vector(v1)
    v2_u = unit_vector(v2)
    angle = np.arccos(np.dot(v1_u, v2_u))
    if math.isnan(angle):
        if (v1_u == v2_u).all():
            return 0.0
        else:
            return np.pi
    return angle

def get_beta_lines(lines):
    newlines=[]
    for i in lines:
        if "beta(" in i:
            newlines.append(i)
    return newlines

def get_beta(lines):
    list=["X","Y","Z"]
    r=[]
    betalines=get_beta_lines(lines)
    for j in list:
        val = 0.0 
        for k in list:
            str1= "beta("+j+";"+k+","+k+")"
            str2= "beta("+k+";"+j+","+k+")"
            str3= "beta("+k+";"+k+","+j+")"
            for i in betalines:
                if str1 in i:
                    val += float(i.split()[9])
                if str2 in i:
                    try:
                        val += float(i.split()[9])
                    except:
                        for s in betalines:
                            if str3 in s:
                                val += float(s.split()[9])
                if str3 in i:
                    try:
                        val += float(i.split()[9])
                    except:
                        for s in betalines:
                            if str2 in s:
                                val += float(s.split()[9])
            allstr = [str1,str2,str3]
        r.append(val)
    return np.array(r)/5

def points2vec(point1,point2):
    vec = np.array(point2)-np.array(point1)
    return vec

def get_perm_dipole(lines):
    for i in lines:
        if " O       :    " in i:
            Ocoord=[]
            for k in [4,7,10]:
                Ocoord.append(float(i.split()[k]))
        if " H       :     4" in i:
            H1coord=[]
            for k in [4,7,10]:
                H1coord.append(float(i.split()[k]))
        if " H       :     7" in i:
            H2coord=[]
            for k in [4,7,10]:
                H2coord.append(float(i.split()[k]))
    a = points2vec(Ocoord,H1coord)
    b = points2vec(Ocoord,H2coord)
#    print 360*angle_between(a,b)/(2*np.pi)
    c = unit_vector(unit_vector(a)+unit_vector(b))
    return c


parser = ArgumentParser(description="My SHG script")
parser.add_argument("-i", "--input",dest="filename", nargs="+", 
                    help="The dalton result file(s)")
parser.add_argument("-d", "--dipole",action="store_true",default=False, dest="dipole", 
                    help="Compute the SHG (beta||) in the direction of the permanent\
 dipole moment (only working for water). Else: z-direction")
parser.add_argument("-p", "--print",action="store_true",default=False, dest="print", 
                    help="Print out more information, for instance filename")
args = parser.parse_args()


for file in args.filename:
    if args.print:
        print file 
    try:
        finp = open(file,"r")
    except:
        exit('Can not open file {0}. Does it exist?'.format(file))

    lines = finp.readlines()
    finp.close()

    betas = get_beta(lines)
    if args.dipole:
        dip = get_perm_dipole(lines)
    else:
        dip = np.array([0.0, 0.0, 1.0])
    print np.dot(betas,dip)


#print "The energy " + sys.argv[1] + " eV corresponds to " + "%.4f" % (1240.0/float(sys.argv[1])) + " nm."
