#!/usr/bin/env python
# Arnfinn Hykkerud Steindal, Tromso Oct. 2013
# Solute in solvent. Make xyz-files of pdb-file

import math
from argparse import ArgumentParser
import sys

def pdb2xyz(line):
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
        quit("something wrong...")
    return math.sqrt(sum([a[i] for i in range(len(a))]))


parser = ArgumentParser(description="My pdb file manipulation script for solute in solvent")

parser.add_argument("-i", "--input",dest="filename", required=True,
                    help="The input file")
parser.add_argument("-xyz", "--xyz",action="store_true",default=False, dest="xyz",
                    help="Make xyz files of solvents and solute")
parser.add_argument("--solxyz",action="store_true",default=False, dest="solxyz",
                    help="Make xyz files of solute")
parser.add_argument("-d", "--mol",action="store_true",default=False, dest="mol",
                    help="Make a dalton mol-file of the solute")
parser.add_argument("-p", "--pdb",dest="pdb",
                    help="Make a pdb-file with given filename of the remaining solvent molecules")
parser.add_argument("-p2", "--pdb2",dest="pdb2",
                    help="Make a pdb-file with given filename of the removed solvent molecules")
parser.add_argument("-r", "--residue",dest="res", default="1",
                    help="The solute residue number")
parser.add_argument("--solute",dest="solute",
                    help="The name of the solute")
parser.add_argument("--solvent",dest="solvent",
                    help="The name of the solvent")
parser.add_argument("-t","--threshold",dest="thres",type=float,
                    help="remove molecules outside a given threshold from the solute atoms")
parser.add_argument("--all",action="store_true",default=False, dest="all",
                    help="Keep all the solvent molecules.")
parser.add_argument("--keep",action="store_true",default=False, dest="keep",
                    help="Keep the head and the tail of the pdb file")
parser.add_argument("-v", "--verbose",action="store_true",default=False, dest="verbose",
                    help="Verbose")

args = parser.parse_args()
file = args.filename
res=args.res
if args.xyz:
    if not args.solute or not args.solvent:
        quit("Please specify solute and solvent if you want to make xyz-files")


infile = open(file,'r')

tofile=""
prot_coord=[]
keep=""

solvent = []
solute = []

# put all the solvent in "solvent"
# and the solute in "solute", as pdb lines
k=-1
prev_res=-999
head = True
pdb_head = ""
pdb_tail = ""
for line in infile.readlines():
    if len(line) > 65:
        if line[0:4]=="ATOM" or line[0:4]=="HETA":
            head = False
            resi = line[22:27].split()[0]
            name = line[17:20]
            if resi==res:
                solute.append(line)
            elif resi == prev_res:
                solvent[k].append(line)
            else:
                prev_res = resi
                k += 1
                solvent.append([])
                solvent[k].append(line)
        elif args.keep:
            if head:
                pdb_head += line
            else:
                pdb_tail += line
    elif args.keep:
        if head:
            pdb_head += line
        else:
            pdb_tail += line


# make xyz of solute
#if args.xyz or args.solxyz:
if args.solxyz:
    tmp_file = open(args.solute + ".xyz","w")
    tmp_text = str(len(solute)) + "\n\n"
    for i in solute:
        tmp_text += pdb2xyz(i)
    tmp_file.write(tmp_text)
    tmp_file.close
    if args.solxyz:
        quit("Only make xyz file of solute!")


reduced_xyz = []
reduced_pdb = []
left_pdb = []
count = 0
for i in solvent:
    store = False
    if args.all:
        store = True
    for j in i:
        if store:
            break
        for k in solute:
            coord_solvent = get_pdbcoord(j)
            coord_solute  = get_pdbcoord(k)
            if get_distance(coord_solvent,coord_solute)<args.thres:
                store = True
                break
        if store:
            break
    if store and len(i)>1:
        count += 1
        if args.xyz:
            tmp_file = open("{0}_{1}.xyz".format(args.solvent,count),"w")
            tmp_text = "{0}\n\n".format(len(i))
            for l in i:
                tmp_text += pdb2xyz(l)
                reduced_xyz.append(pdb2xyz(l))
            tmp_file.write(tmp_text)
            tmp_file.close()
        if args.pdb:
            for l in i:
                reduced_pdb.append(l)
    if not store and len(i)>1:
        if args.pdb2:
            for l in i:
                left_pdb.append(l)
if args.verbose:
    print "Number of solvent molecules kept with threshold {0} angstrom: {1}".format(args.thres,count)

if args.xyz:
    tmp_file = open(args.solvent + "_all.xyz","w")
    tmp_text = str(len(reduced_xyz)) + "\n\n"
    for i in reduced_xyz:
        tmp_text += i
    tmp_file.write(tmp_text)
    tmp_file.close()
if args.pdb:
#    tmp_file = open("{0}_reduced_{1}.pdb".format(args.solute,args.thres),"w")
    tmp_file = open(args.pdb,"w")
    tmp_text = ""
    if args.keep:
        tmp_text += pdb_head
    for i in solute:
        tmp_text += i
    for i in reduced_pdb:
        tmp_text += i
    if args.keep:
        tmp_text += pdb_tail
    tmp_file.write(tmp_text)
    tmp_file.close()

if args.pdb2:
    tmp_file = open(args.pdb2,"w")
    tmp_text = ""
    for i in left_pdb:
        tmp_text += i
    tmp_file.write(tmp_text)
    tmp_file.close()
    


####### NOT IMPLEMENTED YET ############
#make the mol file
if args.mol:
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
