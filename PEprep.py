#!/usr/bin/python
# Arnfinn Hykkerud Steindal, Tromso Jan. 2012
# A script that removes water molecules outside
# a given distance from a protein

import math
from optparse import OptionParser
import sys

def get_xyz(line):
    words=line.split()
    a=len(words)
    return [float(words[a-6]),float(words[a-5]),float(words[a-4])]

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

def new_coord(base,old,new_dist):
    # returns a new coordinate with a distance "new_dist" from point
    # "base" in the same direction as "old"
    old_dist=get_distance(base,old)
    result=[]
    for i in range(len(base)):
        result.append(base[i]+(old[i]-base[i])*new_dist/old_dist)
    return result

parser = OptionParser()
parser.add_option("-i", "--input",dest="filename", help="The input file")
parser.add_option("-t", "--threshold",type="float", dest="thr",  default=8.0, help="The threshold distance for removal of water molecules")
parser.add_option("-n", "--NH",type="float", dest="nh", default=1.009, help="The distance between nitrogen and hydrogen")
parser.add_option("-c", "--CH",type="float", dest="ch", default=1.101, help="The distance between carbon and hydrogen")
# only make QM pdb file
parser.add_option("-q", "--QM",action="store_true",default=False, dest="qm", help="Only make the pdb file of the QM region")
# only make MM pdb file
parser.add_option("-m", "--MM",action="store_true",default=False, dest="mm", help="Only make the pdb file for PE")
# make a dalton molecule file
parser.add_option("-d", "--mol",action="store_true",default=False, dest="mol", help="Make a mol-file for Dalton")
parser.add_option("-a", "--all",action="store_true",default=False, dest="all", help="store only the pdb file after removing water molecules")
parser.add_option("-r", "--residue",dest="residue", help="Add another amino acid residue into the QM region")
(options, args) = parser.parse_args()
file = options.filename
threshold=options.thr
nh=options.nh
ch=options.ch

qm=options.qm
mm=options.mm
mol=options.mol
all=options.all

infile = open(file,'r')

tofile=""
prot_coord=[]
keep=""
for line in infile.readlines():
    if qm:
        tofile=tofile+line
    else:
        words=line.split()
        num=len(words)
        if line[0:4]=="ATOM" or line[0:4]=="HETA":
            if line[21:22]=="A":
                tofile=tofile+line
                if words[2]=="CA" or words[2]=="CA1" or words[2]=="CA2" or words[2]=="CA3":
                    prot_coord.append(get_xyz(line))
            else:
                if words[num-1]!="H":
                    a=get_xyz(line)
                    for i in prot_coord:
                        tmp=get_distance(a,i)
                        if tmp<threshold:
                            tofile=tofile+line
                            if words[num-1]=="O":
                                keep=words[num-7]
                            break
                else:
                    if words[num-7]==keep:
                        tofile=tofile+line

infile.close()

if all:
    b=len(file)
    rmh2ofile = open(file[0:b-4]+'-lessH2O'+file[b-4:b],'w')
    rmh2ofile.write(tofile)
    rmh2ofile.close()
    print "The file " + file[0:b-4]+'-lessH2O'+file[b-4:b] + "created where"
    print "the water molecules outside a threshold of "+str(threshold)
    print "angstrom has been removed."
    sys.exit()

newfile=""
chrom=""

for line in tofile.split("\n"):
    words=line.split()
    num=len(words)
    if num>1:
        if line[0:4]=="ATOM" or line[0:4]=="HETA":
            if line[21:22]=="A":
                if words[5] in ["65","66","67"]:
                    chrom=chrom+line+"\n"
                elif words[5]=="68" and words[2]=="H":
                    chrom=chrom+line+"\n"
                elif words[5]=="64" and words[2]=="O":
                    chrom=chrom+line+"\n"
                elif words[5]=="64" and words[2]=="CA":
                    if not qm:
                        newfile=newfile+line + "\n"
                    line64=line
                    ca64=[float(words[6]),float(words[7]),float(words[8])]
                elif words[5]=="64" and words[2]=="C":
                    chrom=chrom+line+"\n"
                    c64=[float(words[6]),float(words[7]),float(words[8])]
                    new64MM = new_coord(ca64,c64,ch)
                    new64QM = new_coord(c64,ca64,ch)
                    newline2=line64.replace("    C","    H")
                    a=[]
                    b=[]
                    leng=[]
                    for i in range(3):
                        xyz=str(round(new64QM[i],3)).split(".")
                        a.append(xyz[0])
                        b.append(xyz[1])
                        leng.append(4-len(xyz[0]))
                        leng.append(3-len(xyz[1]))
                    newline2=newline2[0:30]+leng[0]*" "+a[0]+"."+b[0]+leng[1]*"0"+leng[2]*" "+a[1]+"."+b[1]+leng[3]*"0"+leng[4]*" "+a[2]+"."+b[2]+leng[5]*"0"+newline2[54:]
                    chrom=chrom+newline2+"\n"

                    newline=line.replace("    C","    H")
                    a=[]
                    b=[]
                    leng=[]
                    for i in range(3):
                        xyz=str(round(new64MM[i],3)).split(".")
                        a.append(xyz[0])
                        b.append(xyz[1])
                        leng.append(4-len(xyz[0]))
                        leng.append(3-len(xyz[1]))
                    newline=newline[0:30]+leng[0]*" "+a[0]+"."+b[0]+leng[1]*"0"+leng[2]*" "+a[1]+"."+b[1]+leng[3]*"0"+leng[4]*" "+a[2]+"."+b[2]+leng[5]*"0"+newline[54:]

                    if not qm:
                        newfile=newfile+newline + "\n"
                elif words[5]=="68" and words[2]=="N":
                    chrom=chrom+line+"\n"
                    n68=[float(words[6]),float(words[7]),float(words[8])]
                    n68line=line
                elif words[5]=="68" and words[2]=="CA":
                    # hopefully last one
                    ca68=[float(words[6]),float(words[7]),float(words[8])]
                    new68MM = new_coord(ca68,n68,ch)
                    new68QM = new_coord(n68,ca68,nh)
                    newline2=line.replace("    C","    H")
                    a=[]
                    b=[]
                    leng=[]
                    for i in range(3):
                        xyz=str(round(new68QM[i],3)).split(".")
                        a.append(xyz[0])
                        b.append(xyz[1])
                        leng.append(4-len(xyz[0]))
                        leng.append(3-len(xyz[1]))
                    newline2=newline2[0:30]+leng[0]*" "+a[0]+"."+b[0]+leng[1]*"0"+leng[2]*" "+a[1]+"."+b[1]+leng[3]*"0"+leng[4]*" "+a[2]+"."+b[2]+leng[5]*"0"+newline2[54:]
                    chrom=chrom+newline2+"\n"

                    newline=n68line.replace("    N","    H")
                    a=[]
                    b=[]
                    leng=[]
                    for i in range(3):
                        xyz=str(round(new68MM[i],3)).split(".")
                        a.append(xyz[0])
                        b.append(xyz[1])
                        leng.append(4-len(xyz[0]))
                        leng.append(3-len(xyz[1]))
                    newline=newline[0:30]+leng[0]*" "+a[0]+"."+b[0]+leng[1]*"0"+leng[2]*" "+a[1]+"."+b[1]+leng[3]*"0"+leng[4]*" "+a[2]+"."+b[2]+leng[5]*"0"+newline[54:]

                    if not qm:
                        newfile=newfile+line + "\n"+newline + "\n"
                else:
                    n=words[1]
                    k=words[5]
                    if not qm:
                        newfile=newfile+line + "\n"
            else:
                newline=line.replace("T3P","HOH")
                if words[num-1]=="O":
                    # n is the atom number
                    n = int(n) + 1
                    # k is the 
                    k = int(k) + 1
                    leng2=5-len(str(k))
                    leng=5-len(str(n))
                    newline = newline[0:6]+ leng*" "+str(n) + newline[11:]
                    newline=newline[0:21]+leng2*" "+str(k) + line[26:] 
                    # .replace(line[22:26],leng2*" "+str(k),1)
#                    newline = newline.replace(line[0:12],"HETATM"+leng*" "+str(n),1)
                    if not qm:
                        newfile=newfile+newline + "\n"
                elif words[num-1]=="H":
                    n = int(n) + 1
                    leng2=5-len(str(k))
                    leng=5-len(str(n))
                    newline = newline[0:6]+ leng*" "+str(n) + newline[11:]
                    newline=newline[0:21]+leng2*" "+str(k) + line[26:] 
#                    leng=5-len(str(n))
#                    newline = newline.replace(line[0:12],"HETATM"+leng*" "+str(n),1)
#                    leng2=5-len(str(k))
#                    newline=newline.replace(line[22:26],leng2*" "+str(k),1)
                    if not qm:
                        newfile=newfile+newline + "\n"
                    
#    else:
#        tofile=tofile+line

print "Done with preparing file "+file
printline=[]
b=len(file)
if not qm:
    rmh2ofile= open(file[0:b-4]+'-PEready'+file[b-4:b],'w')
    rmh2ofile.write(newfile)
    rmh2ofile.close()
    printline.append(file[0:b-4]+'-PEready'+file[b-4:b])

if not mm:
    chromfile= open(file[0:b-4]+'-chrom'+file[b-4:b],'w')
    chromfile.write(chrom)
    chromfile.close()
    printline.append(file[0:b-4]+'-chrom'+file[b-4:b])

if len(printline)==1:
    print "The file "+printline[0]+" has been made."
else:
    print "The files "+printline[0]+" and "+printline[0]+" have been made."

#make the mol file
if mol:
    
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
