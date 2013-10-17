#!/usr/bin/env python
# Arnfinn Hykkerud Steindal, Tromso Oct. 2013
# Solute in solvent. Make xyz-files of pdb-file

import math
from argparse import ArgumentParser
#from optparse import OptionParser
import sys

def get_xyz(line):
    xyz = line[76:78] + 4*" "  +line[31:39] + 4*" " + line[39:47] + 4*" " + line[47:55] + "\n"
    return xyz

def get_pdbcoord(line):
    # return the coordinate of from a pdb line
    return [float(line[31:39]),float(line[39:47]),float(line[47:55])]

def get_xyzcoord(line):
    # return the coordinate of from a xyz line
    words = line.split()
    return [float(words[1]),float(words[2]),float(words[3])]

def get_distance(coord1,coord2):
    a=[]
    if len(coord1)==len(coord2):
        for i in range(len(coord1)):
            vec=coord1[i]-coord2[i]
            vec2=vec*vec
            a.append(vec2)
    else:
        print "something wrong..."
    return math.sqrt(sum([a[i] for i in range(len(a))]))


parser = ArgumentParser(description="My pdb file manipulation script")

parser.add_argument("-i", "--input",dest="filename", help="The input file")
parser.add_argument("-d", "--mol",action="store_true",default=False, dest="mol", help="Make a mol-file of the solute for Dalton")
parser.add_argument("-r", "--residue",dest="res", type=int, default=1, help="The solute residue number")
parser.add_argument("--solute",dest="solute", default="indole", help="The name of the solute")
parser.add_argument("--solvent",dest="solvent", default="water", help="The name of the solvent")
parser.add_argument("-t","--threshold",dest="thres",type=float, default=25.0, 
                    help="remove molecules outside a given threshold from the solute atoms [default: %(default)s]")

args = parser.parse_args()
file = args.filename
res=args.res

mol=args.mol
infile = open(file,'r')

tofile=""
prot_coord=[]
keep=""

res_found = False
all_sol = []
solute = []
old_resi = -999
first = True
for line in infile.readlines():
    if len(line) > 65:
        if line[0:4]=="ATOM" or line[0:4]=="HETA":
            xyzline = get_xyz(line)
            resi = int(line[22:27])
            if resi==res:
                res_found = True
                solute.append(xyzline)
            elif resi == old_resi:
                solvent.append(xyzline)
            else:
                if not first:
                    all_sol.append(solvent)
                first = False
                solvent = []
                solvent.append(str(resi))
                solvent.append(xyzline)
                old_resi = resi
all_sol.append(solvent)

tmp_file = open(args.solute + ".xyz","w")
tmp_text = str(len(solute)) + "\n\n"
for i in solute:
    tmp_text += i
tmp_file.write(tmp_text)
tmp_file.close

reduced_xyz = []
for i in all_sol:
    store = False
    for j in i[1:]:
        for k in solute:
            coord_solvent = get_xyzcoord(j)
            coord_solute  = get_xyzcoord(k)
            if get_distance(coord_solvent,coord_solute)<args.thres:
                store = True
    if store:
        tmp_file = open(args.solvent + "_" + i[0] + ".xyz","w")
        tmp_text = str(len(i)-1) + "\n\n"
        for l in i[1:]:
            tmp_text += l
            reduced_xyz.append(l)
        tmp_file.write(tmp_text)
        tmp_file.close()

tmp_file = open(args.solvent + "_all.xyz","w")
tmp_text = str(len(reduced_xyz)) + "\n\n"
for i in reduced_xyz:
    tmp_text += i
tmp_file.write(tmp_text)
tmp_file.close()


#make the mol file
if mol:
    quit("mol-file making not working yet")
    pdbfile=open(file[0:b-4]+'-chrom'+file[b-4:b],'r')
    lines=pdbfile.readlines()
    atomele=["C","O","N","S","H"]
    atomq  =["6.0","8.0","7.0","16.0","1.0"]
    carbon=[]
    oxygen=[]
    nitrogen=[]
    sulfur=[]
    hydrogen=[]
    all=[carbon,oxygen,nitrogen,sulfur,hydrogen]
    charge=0
    for line in lines:
        try:
            num=int(line[78:79])
            if line[79:80]=="+":
                charge=charge+num
            elif line[79:80]=="-":
                charge=charge-num
        except:
            charge = charge
        coord=[line[31:38],line[39:46],line[47:54]]
        for i in range(5):
            if line[77:78]==atomele[i]:
                all[i].append(coord)
                break
    line1="BASIS\n6-31+G*\n"
    line2="Molfile made from "+file[0:b-4]+'-chrom'+file[b-4:b]+"\n\n"
    line3="Atomtypes=4 Angstrom Nosymmetry"
    if charge!=0:
        line3=line3+" Charge="+str(charge)
    line3=line3+"\n"
    molout=line1+line2+line3
    for i in range(5):
        leng=len(all[i])
        if leng!=0:
            molout=molout+"Charge="+atomq[i]+" Atoms="+str(leng)+"\n"
            for k in range(leng):
                molout=molout+atomele[i]+"   "+all[i][k][0]+"   "+all[i][k][1]+"   "+all[i][k][2]+"\n"
        
    dalfile = open(file[0:b-4]+'.mol','w')
    dalfile.write(molout)
    dalfile.close
    print "The dalton molecule file "+file[0:b-4]+".mol was made"
