#!/usr/bin/python
# Arnfinn Hykkerud Steindal, Tromso Apr 2010; May 2012
# Read a file (-i FILENAME) and make an average of
# values in the first row (if not given as -r ROW).

import sys
import math
from optparse import OptionParser
import re
from numpy import array, cross, pi, cos, arccos as acos
#from cogent.util.array import norm
#from cogent.maths.stats.special import fix_rounding_error

class DihedralGeometryError(Exception): pass
class AngleGeometryError(Exception): pass

def norm(vec):
    """
    calculate the norm of a vector x, y, z
    """
    return math.sqrt(vec[0]*vec[0] + vec[1]*vec[1] + vec[2]*vec[2])

def scalar(v1,v2):
    """
    calculates the scalar product of two vectors
    v1 and v2 are numpy.array objects.
    returns a float for a one-dimensional array.
    """
    return sum(v1*v2)

def angle(v1,v2):
    """
    calculates the angle between two vectors.
    v1 and v2 are numpy.array objects.
    returns a float containing the angle in radians.
    """
    length_product = norm(v1)*norm(v2)
    if length_product == 0:
        raise AngleGeometryError(\
        "Cannot calculate angle for vectors with length zero")
    angle = acos(scalar(v1,v2)/length_product)
    return angle

def create_vector(vec):
    """Returns a vector as a numpy array."""
    return array([vec[0],vec[1],vec[2]])
    
def create_vectors(vec1,vec2,vec3,vec4):
    """Returns dihedral angle, takes four
    Scientific.Geometry.Vector objects
    (dihedral does not work for them because
    the Win and Linux libraries are not identical.
    """
    return map(create_vector,[vec1,vec2,vec3,vec4])

def dihedral(vec1,vec2,vec3,vec4):
    """
    Returns a float value for the dihedral angle between 
    the four vectors. They define the bond for which the 
    torsion is calculated (~) as:
    V1 - V2 ~ V3 - V4 

    The vectors vec1 .. vec4 can be array objects, lists or tuples of length 
    three containing floats. 
    For Scientific.geometry.Vector objects the behavior is different 
    on Windows and Linux. Therefore, the latter is not a featured input type 
    even though it may work.
    
    If the dihedral angle cant be calculated (because vectors are collinear),
    the function raises a DihedralGeometryError
    """    
    # create array instances.
    v1,v2,v3,v4 =create_vectors(vec1,vec2,vec3,vec4)
    all_vecs = [v1,v2,v3,v4]

    # rule out that two of the atoms are identical
    # except the first and last, which may be.
    for i in range(len(all_vecs)-1):
        for j in range(i+1,len(all_vecs)):
            if i>0 or j<3: # exclude the (1,4) pair
                equals = all_vecs[i]==all_vecs[j]
                if equals.all():
                    raise DihedralGeometryError(\
                        "Vectors #%i and #%i may not be identical!"%(i,j))

    # calculate vectors representing bonds
    v12 = v2-v1
    v23 = v3-v2
    v34 = v4-v3

    # calculate vectors perpendicular to the bonds
    normal1 = cross(v12,v23)
    normal2 = cross(v23,v34)

    # check for linearity
    if norm(normal1) == 0 or norm(normal2)== 0:
        raise DihedralGeometryError(\
            "Vectors are in one line; cannot calculate normals!")

    # normalize them to length 1.0
    normal1 = normal1/norm(normal1)
    normal2 = normal2/norm(normal2)

    # calculate torsion and convert to degrees
    torsion = angle(normal1,normal2) * 180.0/pi

    # take into account the determinant
    # (the determinant is a scalar value distinguishing
    # between clockwise and counter-clockwise torsion.
    if scalar(normal1,v34) >= 0:
        return torsion
    else:
        torsion = 360-torsion
        if torsion == 360: torsion = 0.0
        return torsion
#    return torsion



def aver(mylist):
    tot = 0.0
    for i in mylist:
        tot=tot+i
    return tot/len(mylist)

def stdev(mylist):
    ave = aver(mylist)
    stan=0.0
    for i in mylist:
        stan=stan+(i-ave)*(i-ave)
    return math.sqrt(stan/(len(mylist)-1))

def ev2nm(mylist):
    newlist=[]
    for i in mylist:
        newlist.append(1240.0/i)
    return newlist

def get_distance(coord1,coord2):
    """
    Return the distance between two points
    """
    a=[]
    if len(coord1)==len(coord2):
        for i in range(len(coord1)):
            vec=coord1[i]-coord2[i]
            vec2=vec*vec
            a.append(vec2)
    else:
        print "something wrong..."
    return math.sqrt(sum([a[i] for i in range(len(a))]))
def get_angle(a,b,c):
    """
    Get the angle between three atoms/coordinates
    """
    return math.degrees(angle(create_vector([a[0]-b[0],a[1]-b[1],a[2]-b[2]]),create_vector([c[0]-b[0],c[1]-b[1],c[2]-b[2]])))

def get_dihedral(a,b,c,d):
#    return dihedral(get_vec(a,b),get_vec(b,c),get_vec(c,d),get_vec(a,b))
    return dihedral(a,b,c,d)

def get_vec(a,b):
    return create_vector([a[0]-b[0],a[1]-b[1],a[2]-b[2]])

def print_dist(a,b,c,d):
    print a + " - " + c + " distance "+str(get_distance(b,d)) 

parser = OptionParser()
parser.add_option("-i", "--input",dest="filename", help="the file to read")
parser.add_option("-r", "--row",type="int", dest="row",  default=1, help="The row where numbers are located")
parser.add_option("-d", "--decimals",type="int", dest="dec", default=4, help="Number of decimals in the printet numbers")
parser.add_option("-p", "--print",action="store_true", default=False, dest="printing", help="Print all the values")
parser.add_option("--ev2nm",action="store_true", default=False, dest="ev2nm", help="Convert from eV to nm before calculating average")
parser.add_option("--av2",action="store_true", default=False, dest="aver2", help="Calculate the average of numbers where two are weighted")
parser.add_option("--avnum",type="int", dest="avernum", default=0,help="Calculate the average of the N first values")
(options, args) = parser.parse_args()
file = open(options.filename,'r')
row = options.row-1
dec = str(options.dec)

fps = ["GFP","YFP","EFP","CFP","BFP"]
gfpatoms=["N1","CA1","C1","CB1","OG","N2","CA2","C2","O2","CB2","CG2","CD1","CD2","CE1","CE2","CZ","OH","N3","CA3","C3","O3","ND1","NE2","NE1","CZ2","CH2","CZ3","CE3"]
lines=file.readlines()
for line in lines:
    words = line.split()
    if words[0]=="HETATM":
        if words[3] in fps:
            setattr(sys.modules[__name__],"FP",words[3])
            if words[2] in gfpatoms:
                setattr(sys.modules[__name__],words[2],[float(words[6]),float(words[7]),float(words[8])])

print "Filename: " + options.filename
if FP in ["GFP","YFP","EFP"]:
    print_dist("OH",OH,"CZ",CZ)
    print_dist("CZ",CZ,"CE1",CE1)
    print_dist("CZ",CZ,"CE2",CE2)
    print_dist("CE1",CE1,"CD1",CD1)
    print_dist("CE2",CE2,"CD2",CD2)
    print_dist("CD1",CD1,"CG2",CG2)
if FP == "BFP":
    print_dist("NE2",NE2,"CD2",CD2)
    print_dist("NE2",NE2,"CE1",CE1)
    print_dist("CE1",CE1,"ND1",ND1)
    print_dist("ND1",ND1,"CG2",CG2)
if FP == "CFP":
    print_dist("CH2",CH2,"CZ2",CZ2)
    print_dist("CH2",CH2,"CZ3",CZ3)
    print_dist("CZ2",CZ2,"CE2",CE2)
    print_dist("CZ3",CZ3,"CE3",CE3)
    print_dist("CE3",CE3,"CD2",CD2)
    print_dist("CE2",CE2,"CD2",CD2)
    print_dist("CE2",CE2,"NE1",NE1)
    print_dist("NE1",NE1,"CD1",CD1)
    print_dist("CD1",CD1,"CG2",CG2)
if FP in fps:
    print_dist("CD2",CD2,"CG2",CG2)
    print_dist("CG2",CG2,"CB2", CB2)
    print_dist("CB2",CB2,"CA2", CA2)
    print_dist("CA2",CA2,"N2" , N2 )
    print_dist("N2", N2 ,"C1" , C1 )
    print_dist("C1", C1 ,"N3" , N3 )
    print_dist("N3", N3 ,"C2" , C2 )
    print_dist("C2", C2 ,"O2" , O2 )
    print_dist("C2", C2 ,"CA2", CA2)
    print_dist("C1", C1 ,"CA1", CA1)
    print_dist("N3", N3 ,"CA3", CA3)
if FP in ["GFP","YFP","EFP","CFP"]:
    print "CD1 - CG2 - CB2 angle " + str(get_angle(CD1,CG2,CB2)) 
if FP == "BFP":
    print "ND1 - CG2 - CB2 angle " + str(get_angle(ND1,CG2,CB2)) 
if FP in fps:
    print "CD2 - CG2 - CB2 angle " + str(get_angle(CD2,CG2,CB2)) 
    print "CG2 - CB2 - CA2 angle " + str(get_angle(CG2,CB2,CA2)) 
    print "CB2 - CA2 - C2 angle " + str(get_angle(CB2,CA2,C2))   
    print "CB2 - CA2 - N2 angle " + str(get_angle(CB2,CA2,N2))   
if FP in ["GFP","YFP","EFP","CFP"]:
    print "CD1 CG2 CB2 CA2 dihedral "+ str(get_dihedral(CD1,CG2,CB2,CA2))
if FP == "BFP":
    print "ND1 CG2 CB2 CA2 dihedral "+ str(get_dihedral(ND1,CG2,CB2,CA2))
if FP in fps:
    print "CD2 CG2 CB2 CA2 dihedral "+ str(get_dihedral(CD2,CG2,CB2,CA2))
    print "CG2 CB2 CA2 N2 dihedral "+ str(get_dihedral(CG2,CB2,CA2,N2))
    print "CG2 CB2 CA2 C2 dihedral "+ str(get_dihedral(CG2,CB2,CA2,C2))



#if options.avernum>0:
#    lines = file.readlines()[0:options.avernum]
#else:
#    lines = file.readlines()
#tab=[]

#for line in lines:
#    words = line.split()
#    if options.aver2:
#        oneex = float(re.sub("\D","",words[0].split(".")[0])+"."+re.sub("\D","",words[0].split(".")[1]))
#        onetr = float(re.sub("\D","",words[1].split(".")[0])+"."+re.sub("\D","",words[1].split(".")[1]))
#        twoex = float(re.sub("\D","",words[2].split(".")[0])+"."+re.sub("\D","",words[2].split(".")[1]))
#        twotr = float(re.sub("\D","",words[3].split(".")[0])+"."+re.sub("\D","",words[3].split(".")[1]))
#        ettall=str((oneex*onetr + twoex*twotr)/(onetr + twotr))
##        print"two"+ettall
#    else:
#        ettall = words[row]
##        print"one" +ettall
#    if"." in ettall:
#        ettall = float(re.sub("\D","",ettall.split(".")[0])+"."+re.sub("\D","",ettall.split(".")[1]))
##        ettall = float(re.sub("\D","",words[row].split(".")[0])+"."+re.sub("\D","",words[row].split(".")[1]))
#    else:
#        ettall = float(re.sub("\D","",ettall))
##        ettall = float(re.sub("\D","",words[row]))
#    if options.printing:
#        print ettall
#    tab.append(ettall)
#
#if options.ev2nm:
#    tab = ev2nm(tab)
    
#ave = aver(tab)
#stan = stdev(tab)
#
#print"Number of values ="+str(len(tab))
#string ="Average value = %."+dec+"f"
#print string % (ave)
#string ="Standard deviation = %."+dec+"f"
#print string % (stan)
