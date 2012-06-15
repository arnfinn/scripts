#!/usr/bin/python

# Arnfinn Hykkerud Steindal, Tromso June 2012
# A script that moves water molecules from the PE
# region to the QM region when inside
# a given distance from the qm region
# INPUT: -q mol file; -m pot file

import math
#from optparse import OptionParser
import optparse

class OptionParser (optparse.OptionParser):
    def check_required (self, opt):
        option = self.get_option(opt)
        # Assumes the option's 'default' is set to None!
        if getattr(self.values, option.dest) is None:
            self.error("%s option not supplied" % option)

def get_xyz(line):
    words=line.split()
    return [float(words[1]),float(words[2]),float(words[3])]

def get_distance(coord1,coord2):
    a=[]
    if len(coord1)==len(coord2):
        for i in range(len(coord1)):
            vec=float(coord1[i])-float(coord2[i])
            vec2=vec*vec
            a.append(vec2)
    else:
        print "something wrong..."
    return math.sqrt(sum([a[i] for i in range(len(a))]))

def mkmolline(ele,x,y,z):
    n=10
    a=n-len(x)
    b=n-len(y)
    c=n-len(z)
    return ele + a*" " + x + b*" " + y + c*" " + z 

parser = OptionParser()
parser.add_option("-q", "--qminput",dest="qmfile", default=None)
parser.add_option("-m", "--mminput",dest="mmfile", default=None)
parser.add_option("-t", "--threshold",type="float", dest="thr",  default=4.0)

(options, args) = parser.parse_args()
parser.check_required("-q")
parser.check_required("-m")

thr=options.thr
qmfile=open(options.qmfile,'r')
mmfile=open(options.mmfile,'r')
qmlen=len(options.qmfile)
mmlen=len(options.mmfile)

heavyatom=[]
lines=qmfile.readlines()
for line in lines[4:]:
    atm=line.split()[0]
    if atm in ["C","N","O","H"]:
        heavyatom.append(get_xyz(line))
    

k=0
r=3
numh2o=0
moloxyz=[]
molhxyz=[]
new_pot=""
for line in mmfile.readlines():
    k=k+1
    words=line.split()
    if k==1:
        firline=line
    elif k==2:
        sites=int(words[0])
        exlist=int(words[3])
        try:
            first=int(words[4])
            tot=exlist+first
        except:
            tot=exlist
        if exlist>10:
            exlist=10
        secline=line
    elif k>2 and len(words)>10:
        test=0
        for i in range(exlist-3):
            test=test+int(words[i+4])
        if test==0 and words[tot-1]=="8":
            xyz=[]
            # we are probably at a water molecule...
            for j in range(3):
                test=words[tot+j].split(".")
                a=3-len(test[0])
                xyz.append(a*" "+test[0]+"."+test[1][0:3])
            mindist = 10.0
            for j in heavyatom:
                dist = get_distance(xyz,j)
                if dist<mindist:
                    mindist=dist
#            mindist=min(get_distance(xyz,oh_coord),get_distance(xyz,n2_coord),get_distance(xyz,o2_coord))
            if mindist<thr:
                numh2o=numh2o+1
                moloxyz.append(xyz)
                r=0
            else:
                new_pot=new_pot+line
        elif r<2:
            xyz=[]
            # we are probably at a water molecule...
            for j in range(3):
                test=words[tot+j].split(".")
                a=3-len(test[0])
                xyz.append(a*" "+test[0]+"."+test[1][0:3])
            molhxyz.append(xyz)
            r=r+1
        else:
            new_pot=new_pot+line

oldnum=int(secline.split()[0])
newnum=oldnum-3*numh2o

newsecline=" "+ str(newnum)
for i in secline.split()[1:]:
    newsecline=newsecline + " " + i

newpot=open(options.mmfile[0:mmlen-4]+"-new.pot","w")
newpot.write(firline+newsecline+"\n"+new_pot+"\n")
newpot.close()

#make new mol file
mol=True
if mol:
    atomele=["C","O","N","S","H"]
    atomq  =["6.0","8.0","7.0","16.0","1.0"]
    carbon=[]
    oxygen=[]
    nitrogen=[]
    sulfur=[]
    hydrogen=[]
    all=[carbon,oxygen,nitrogen,sulfur,hydrogen]
    charge=0
    if lines[0][0:5] == "BASIS":
        head = 5
    elif lines[0][0:5] == "ATOMB":
        head = 4
    for line in lines[head:]:
        words = line.split()
        for i in range(5):
            if words[0]==atomele[i]:
                coord=[words[1],words[2],words[3]]
                all[i].append(coord)
                break
    molout=""
    for line in lines[0:head]:
        molout = molout + line
    for i in range(5):
        leng=len(all[i])
        if atomele[i]=="O":
            leng=leng+numh2o
            for l in range(numh2o):
                all[i].append([str(moloxyz[l][0]),moloxyz[l][1],moloxyz[l][2]])
        if atomele[i]=="H":
            leng=leng+2*numh2o
            for l in range(2*numh2o):
                all[i].append(molhxyz[l])
        if leng!=0:
            molout=molout+"Charge="+atomq[i]+" Atoms="+str(leng)+"\n"
            for k in range(leng):
                molout=molout+mkmolline(atomele[i],all[i][k][0],all[i][k][1],all[i][k][2])+"\n"
        
    dalfile = open(options.qmfile[0:qmlen-4]+'-new.mol','w')
    dalfile.write(molout)
    dalfile.close
qmfile.close()
mmfile.close()

print numh2o
