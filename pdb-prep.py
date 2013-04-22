#!/usr/bin/env python
# Arnfinn Hykkerud Steindal, Tromso March 2013
# A script for pdb manipulations

import math
#from optparse import OptionParser
from argparse import ArgumentParser
import sys

def get_xyz(line):
    words=line.split()
    a=len(words)
    return [float(words[a-6]),float(words[a-5]),float(words[a-4])]

class CoordManipulation:
    def __init__(self,coord1,coord2):
        self.coord1 = coord1
        self.coord2 = coord2

    def get_distance(self):
        a=[]
        if len(self.coord1)==len(self.coord2):
            for i in range(len(self.coord1)):
                vec=self.coord1[i]-self.coord2[i]
                vec2=vec*vec
                a.append(vec2)
        else:
            print "something wrong..."
        return math.sqrt(sum([a[i] for i in range(len(a))]))

    def new_coord(new_dist=1.101):
        # returns a new coordinate with a distance "new_dist" from point
        # "coord1" in the same direction as "coord2"
        old_dist=self.get_distance(self.coord1,self.coord2)
        result=[]
        for i in range(len(self.coord1)):
            result.append(self.coord1[i]+(self.coord2[i]-self.coord1[i])*new_dist/old_dist)
        return result


class pdbCutter(CoordManipulation):
    # cut out amino acids from a pdb file and cap the endings
    # returns two pdb files?
    def __init__(self, file=None, res=[66], size="small"):
        self.filename = file
        self.res = res
        self.size = size
        self.open = False
        print self.res
        print self.filename
#        self.clean = self.pdbcleaner(self.lines)

    def get_lines(self,finp=None):
        if finp is None:
            finp = self.filename
        if not self.open:
            try:
                myfile=open(finp,'r')
            except:
                exit('Can not open file {0}. Does it exist?'.format(finp))
            self.lines = myfile.readlines()
            myfile.close()
            self.open = True
        else:
            pass

    def get_element(self,pdbstring):
        return pdbstring[77]
        
    def get_typ(self,pdbstring):
        return pdbstring[0:6].split()[0]

    def get_atom(self,pdbstring):
        return pdbstring[13:17].split()[0]

    def get_residue(self,pdbstring):
        return int(pdbstring[23:26].split()[0])

    def get_coord(self,pdbstring):
        x = float(pdbstring[30:38])
        y = float(pdbstring[38:46])
        z = float(pdbstring[46:54])
        return [x,y,z]

    def pdbcleaner(self,oldlines=None):
        if oldlines is None:
            oldlines = self.lines
        newline=[]
        for i in oldlines:
            if self.check_string(i):
                newline.append(i)
        return newline

    def pdb2xyz(self,pdblines=None,cntr=True,cleaned=False):
        if pdblines is None:
            pdblines = self.lines
        if cleaned:
            cleanlines = pdblines
        else:
            cleanlines=pdbcleaner(pdblines)
        k=0
        body=""
        for i in cleanlines:
            k+=1
            if cntr:
                a=5-len(k)
                line=i[77]+str(k)+a*' '+i[30:38]+'   '+i[38:46]+'   '+i[46:54]+'\n'
            else:
                line=i[77]+'    '+i[30:38]+'   '+i[38:46]+'   '+i[46:54]+'\n'
            body=body+line
        return str(k)+"\n\n"+body

    def wrtxyz(self,pdblines=None,filename=None,cntr=True):
        if filename is None:
            filename = self.filename
        if pdblines is None:
            pdblines = self.lines
        a=len(filename)
        out=open(filename[0:a-4]+'.xyz','w')
        out.write(self.pdb2xyz(pdblines=pdblines,cntr=cntr))
        out.close()

    def check_string(self, pdbstring):
        # check if string is a "pdb string"
        if len(pdbstring)>77:
            test1=self.get_typ(pdbstring)
            if test1!="ATOM" and test1!="HETATM":
                return False
            else:
                try:
                    test2=self.get_residue(pdbstring)
                    test3=self.get_coord(pdbstring)
                    return True
                except:
                    return False
        else:
            return False

    def cutter(self):
        for i in self.lines:
            pass

    def cutout(self):
#        self.small=small
        self.minus_coord = self.cap_coord("minus")
        self.plus_coord = self.cap_coord("plus")

        self.newlines = ""

        for i in self.lines:
            if not self.check_string(i):
#                print i
                continue
            try:
                resline = self.get_residue(i)
                coord = self.get_coord(i)
            except:
                exit("something wrong with line: ", i)
            if resline==self.res:
                self.newlines+=i
            elif resline==self.res-1:
                atom=i[13:16]
                if atom=="O  ":
                    self.newlines+=i
                elif atom=="C  ": 
                    self.newlines+=i
                    if self.small:
                        c_neg = coord
                elif atom=="CA ": 
                    ca_neg = coord
                    if self.small:
                        pass
                elif self.small:
                    
                    pass
                else:
                    pass
            elif resline==self.res+1:
                atom=i[13:16]
                if atom=="N  ":
                    self.newlines+=i
                elif atom=="H  ":
                    self.newlines+=i
                
                    
        return self.newlines

class pdbPrep:
    def __init__(self,pdbstring):
        # default values
        self.lines=pdbstring
        self.res = 66
        self.small = True

    def check_string(self, pdbstring):
        # check if string is a "pdb string"
        if len(pdbstring)>77:
            test1=self.get_typ(pdbstring)
            if test1!="ATOM" and test1!="HETATM":
                return False
            else:
                try:
                    test2=self.get_residue(pdbstring)
                    test3=self.get_coord(pdbstring)
                    return True
                except:
                    return False
        else:
            return False

    

    def def_cut_input(self,lines,res,small):
        self.lines=lines
        try:
            self.res = int(res)
        except:
            exit("input {0} not an integer".format(res))

        self.small = small

    def cap_coord(self,side):
        self.side = side
        if self.side == "minus":
            self.resi= int(self.res)-1
        elif self.side == "plus":
            self.resi= int(self.res)+1
        else:
            exit("something wrong...")

        for i in self.lines:
#            print i
            if not self.check_string(i):
                continue
            residue = self.get_residue(i)
            if residue != self.res - 1 and residue != self.res + 1:
                continue
            atmname = self.get_atom(i)
            if self.small:
                capside = "C"
                conside = "CA"
            else:
                common = ""
                capsid = "CA"
            if atmname == common:
                pass
            if residue == self.res - 1:
                pass

            if self.side =="minus":
                print "test"
        return [0.0,0.0]

    def cutout(self):
#        self.small=small
        

        self.minus_coord = self.cap_coord("minus")
        self.plus_coord = self.cap_coord("plus")

        self.newlines = ""

        for i in self.lines:
            if not self.check_string(i):
#                print i
                continue
            try:
                resline = self.get_residue(i)
                coord = self.get_coord(i)
            except:
                exit("something wrong with line: ", i)
            if resline==self.res:
                self.newlines+=i
            elif resline==self.res-1:
                atom=i[13:16]
                if atom=="O  ":
                    self.newlines+=i
                elif atom=="C  ": 
                    self.newlines+=i
                    if self.small:
                        c_neg = coord
                elif atom=="CA ": 
                    ca_neg = coord
                    if self.small:
                        pass
                elif self.small:
                    
                    pass
                else:
                    pass
            elif resline==self.res+1:
                atom=i[13:16]
                if atom=="N  ":
                    self.newlines+=i
                elif atom=="H  ":
                    self.newlines+=i
                
                    
        return self.newlines


    def pdb2mol(self):
        charge=0
        for i in self.lines:
            if i[0:6]=='HETATM' or i[0:4]=='ATOM':
                k=k+1
                line="{0}{1}   {2}   {3}   {4}\n".format(
                    i[77],k,i[30:38],i[38:46],i[46:54])
                body=body+line
                try:
                    if i[79]=="+":
                        charge+=1
                    elif i[79]=="-":
                        charge-=1
                except:
                    pass
            



parser = ArgumentParser(description="My pdb manipulation script")
parser.add_argument("-i", "--input",dest="filename", 
                    help="The pdb input file")
parser.add_argument("-r", "--residue",dest="res", nargs="+", default = ["6"], 
                    help="Residues to extract from pdb file")
parser.add_argument("-s", "--split", action="store_true", dest="split", default=False, 
                    help="Split the extracted pdb files into separat files")
parser.add_argument("-c", "--capping",dest="cap", metavar="CAPTYPE", default="small",
                    help="How to cap the residue(s), small (s) or large/l")
parser.add_argument("--rmh2o", action="store_true", dest="rmwater", default=False, 
                    help="Remove water molecules outside a given threshold")




parser.add_argument("-t", "--threshold",type=float, dest="thr",  default=8.0, 
                    help="The threshold distance for removal of water molecules")
parser.add_argument("-n", "--NH",type=float, dest="nh", default=1.009, 
                    help="The distance between nitrogen and hydrogen")
parser.add_argument("--CH",type=float, dest="ch", default=1.101, 
                    help="The distance between carbon and hydrogen")
# only make QM pdb file
parser.add_argument("--QM",action="store_true",default=False, dest="qm", 
                    help="Only make the pdb file of the QM region")
# only make MM pdb file
parser.add_argument("-m", "--MM",action="store_true",default=False, dest="mm", 
                    help="Only make the pdb file for PE")
# make a dalton molecule file
parser.add_argument("-d", "--mol",action="store_true",default=False, dest="mol", 
                    help="Make a mol-file for Dalton")
parser.add_argument("-a", "--all",action="store_true",default=False, dest="all", 
                    help="store only the pdb file after removing water molecules")
args = parser.parse_args()


file = args.filename
threshold=args.thr
res=args.res
prev=""
next=""
if args.cap =="small":
    small=True
else:
    small=False

try:
    finp = open(file,"r")
except:
    exit('Can not open file {0}. Does it exist?'.format(file))
#lines=finp.readlines()

test=pdbCutter(file=file)
test2 = pdbCutter(res=[65,64])


test.get_lines()


#for i in args.res:
#    test.def_cut_input(finp.readlines(),i,small)
#    print test.cutout()

'''
try:
    if args.res:
        prev=str(int(res)-1)
        next=str(int(res)+1)
except:
    print "The residue has to be an integer: -r <integer>"
    sys.exit()
    
nh=args.nh
ch=args.ch

qm=args.qm
mm=args.mm
mol=args.mol
all=args.all

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
                # The chromophore
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
                # extra amino acid
                elif words[5] in [res]:
                    chrom=chrom+line+"\n"
                elif words[5]==next and words[2]=="H":
                    chrom=chrom+line+"\n"
                elif words[5]==prev and words[2]=="O":
                    chrom=chrom+line+"\n"
                elif words[5]==prev and words[2]=="CA":
                    if not qm:
                        newfile=newfile+line + "\n"
                    line64=line
                    ca64=[float(words[6]),float(words[7]),float(words[8])]
                elif words[5]==prev and words[2]=="C":
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
                elif words[5]==next and words[2]=="N":
                    chrom=chrom+line+"\n"
                    n68=[float(words[6]),float(words[7]),float(words[8])]
                    n68line=line
                elif words[5]==next and words[2]=="CA":
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
'''
