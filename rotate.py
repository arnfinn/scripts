#!/usr/bin/env python 
# Arnfinn Hykkerud Steindal, Tromso March 2011 
# Move and rotate a molecule so the first atom is in origin, the second
# atom is along the z-axis and the third atom is in the yz-plane.
# Based on rotmol.py from Feb. 2009 and rotate_xyz.py 

import sys
import math
import argparse

def rotation(vec,ang,round):
    # Rotate a vector 'vec' around the vector 'round' by 'ang'
    # degrees. The rotation, according to:
    # http://en.wikipedia.org/wiki/Rodrigues%27_rotation_formula
    x=vec[0]*math.cos(ang)+math.sin(ang)*(vec[2]*round[1]-vec[1]*round[2])+(1-math.cos(ang))*(vec[0]*round[0]*round[0]+vec[1]*round[0]*round[1]+vec[2]*round[0]*round[2])
    y=vec[1]*math.cos(ang)+math.sin(ang)*(vec[0]*round[2]-vec[2]*round[0])+(1-math.cos(ang))*(vec[0]*round[1]*round[0]+vec[1]*round[1]*round[1]+vec[2]*round[1]*round[2])
    z=vec[2]*math.cos(ang)+math.sin(ang)*(vec[1]*round[0]-vec[0]*round[1])+(1-math.cos(ang))*(vec[0]*round[2]*round[0]+vec[1]*round[2]*round[1]+vec[2]*round[2]*round[2])
    return [x,y,z]

def dot_product(a, b):
    if len(a)!=len(b):
        print 'vectors not of same length in dot_product'
        exit()
    return sum([a[i]*b[i] for i in range(len(a))])

def vec_len(a):
    return math.sqrt(sum([a[i]*a[i] for i in range(len(a))]))

def vec_sub(a,b):
    if len(a)!=len(b):
        print 'vectors not of same length in vec_sub'
        exit()
    c = []
    for i in range(len(a)):
        c.append(a[i] - b[i])
    return c

def angle(a,b):
    return math.acos(dot_product(a,b)/(vec_len(a)*vec_len(b)))

def dist_origin(a,b):
    a = str(vec_len(a))
    b = str(vec_len(b))
    if a!=b:
        print 'The distance between atom and origin changed after rotation!'
        print 'Distance before rotation: '+a
        print 'Distance after rotation: '+b
        print 'The rotation of the molecule was not successful'
        exit()
    return

def rotarg(a,b,c):
    # The arguments for the first rotation
    vec1=vec_sub(b,a)
    if round(vec1[0],8)!=0.0 and round(vec1[1],8)!=0.0:
        # make rotation axis [y,-x,0.0] and angle to rotate around this
        # axis so atom 2 is along z axis. Only done if the atom is not
        # along the z-axis already.
        leng=vec_len([vec1[0],vec1[1],0.0])
        rotvec1=[vec1[1]/leng, -vec1[0]/leng, 0.0]
        angle1= angle(vec1,[0.0,0.0,1.0])
        # Check if the rotation is correct:
        rot1=rotation(vec1,angle1,rotvec1)
        if round(rot1[0],8)!=0.0 or round(rot1[1],8)!=0.0:
            print 'Something wrong. The second atom is not'
            print 'located at x,y = 0.0! Fix script.'
            exit()
    # The arguments for the second rotation
    else:
        angle1=0.0
        rotvec1=[1.0,0.0,0.0]
    vec2=vec_sub(c,a)
    if round(vec2[0],8)!=0.0:
        # Make rotation so the three first atoms are located in a plane
        # Original vector of the third atom in the xy-plane:
        new_vec=rotation(vec2,angle1,rotvec1)
        A=[new_vec[0],new_vec[1],0.0]
        B=[0.0,1.0,0.0]
        angle2=angle(A,B)
        # Vector to rotate around. Test to see if the rotation is
        # clockwise or counter-clockwise:
        rot1=rotation(new_vec,angle2,[0.0,0.0,1.0])
        rot2=rotation(new_vec,angle2,[0.0,0.0,-1.0])
        if (round(rot1[0],10)!=0.0) and (round(rot2[0],10)!=0.0):
            print 'Atom nr 3 is not located at x eq. 0.0'
            print 'but at '+str(rot1[0])+' or '+str(rot2[0])
        if (math.fabs(rot1[0])>math.fabs(rot2[0])):
            w=-1.0
        elif (math.fabs(rot1[0])<math.fabs(rot2[0])):
            w=1.0
        rotvec2=[0.0,0.0,w]
    else:
        angle2=0.0
        rotvec2=[1.0,0.0,0.0]
    return [angle1,rotvec1],[angle2,rotvec2]

parser = argparse.ArgumentParser(
    formatter_class=argparse.RawTextHelpFormatter,
    description="\
Script for rotating and moving molecules in an xyz file")

parser.add_argument("-i", "--input",dest="filename")
parser.add_argument("-r", "--rotatm",
                  dest="a", nargs=3, default=[1,2,3])
args = parser.parse_args()

file = args.filename
b=len(file)
c=2 #File starting with two empty lines is default

# This script may work with dalton molecule files
if file[b-3:b]=='xyz':
    c=2
elif file[b-3:b]=='mol':
    c=4

infile = open(file,'r')
wrfile = open(file[0:b-4]+'_rot'+file[b-4:b],'w')
lines=infile.readlines()

# The three reference atoms. 
atoms= args.a
if atoms == None:
    atoms=[1,2,3]
atmlist=['O','C','H','N','S']

coor=[]
for i in range(3):
    a=lines[atoms[i]+c-1].split()
    coor.append([float(a[1]),float(a[2]),float(a[3])])
orig = coor[0]
[angle1,rotvec1],[angle2,rotvec2] = rotarg(coor[0],coor[1],coor[2])

for line in lines:
    words=line.split()
    try:
        atm = words[0]
    except:
        wrfile.write(line)
        continue
    if atm[0] in atmlist and len(atm)<6:
        coor=[float(words[1]),float(words[2]),float(words[3])]
        # Move the molecule to origin
        vec1=vec_sub(coor,orig)
        # The first rotation
        new_vec=rotation(vec1,angle1,rotvec1)
        dist_origin(vec1,new_vec)
        # The second rotation
        new_vec=rotation(new_vec,angle2,rotvec2)
        dist_origin(vec1,new_vec)
        # write to new xyz-file
        a=4-len(words[0])
        wrline = words[0]+a*' '
        for i in range(3):
            val=str(round(new_vec[i],10))
            a=16-len(val)
            wrline = wrline + a*' ' + str(val)
        wrline=wrline+'\n'
        wrfile.write(wrline)
    else:
        wrfile.write(line)
wrfile.close()
infile.close()
