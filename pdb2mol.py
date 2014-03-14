#!/usr/bin/python
# Arnfinn Hykkerud Steindal, Tromso Dec 2011
# Make a xyz file out of a pdb file

import sys
from optparse import OptionParser

parser = OptionParser()
parser.add_option("-i", "--input",dest="filename", help="the file to read")
parser.add_option("-b", "--basis",dest="basisset", default='6-31+G*', help="the basisset")
(options, args) = parser.parse_args()
basis = options.basisset
pdbfile = open(options.filename,'r')
lines=pdbfile.readlines()
pdbfile.close()

k=0
body=''
charge=0
for i in lines:
    if i[0:6]=='HETATM' or i[0:4]=='ATOM':
        k=k+1
        line=i[77]+str(k)+'   '+i[30:38]+'   '+i[38:46]+'   '+i[46:54]+'\n'
        body=body+line
        try:
            if i[79]=="+":
                charge=charge+1
            elif i[79]=="-":
                charge=charge-1
        except:
            charge=charge

#out.write(str(k)+'\n'+str(charge)+'\n'+body)

xyzfile=str(k)+'\n\n'+body

all   = [['C','',0,'6.0'],['N','',0,'7.0'],['O','',0,'8.0'],['S','',0,'16.0'],['H','',0,'1.0']]
fact  = len(all)
inp=xyzfile.split('\n')

for i in inp:
    words = i.split()
    for j in range(fact):
        try:
            atom=words[0][0]
            if atom== all[j][0]:
                newline=words[0]+fact*' '+words[1]+fact*' '+'\
'+words[2]+fact*' '+words[3]+'\n'
                all[j][1] = all[j][1] + newline
                all[j][2] = all[j][2] + 1
        except:
            break

atmtps = 0
for j in range(fact):
    if all[j][2]>0:
        atmtps = atmtps + 1

a=len(options.filename)
mol=open(options.filename[0:a-4]+'.mol','w')
mol.write('BASIS\n\
'+basis+'\n\
Structure from file '+options.filename+'\n\
----------------------\n\
AtomTypes='+str(atmtps)+' NoSymmetry Angstrom')
if charge==0:
    mol.write('\n')
else:
    print "WARNING!"
    print "The total charge of the molecule(s) is (are)"
    print "found to be "+str(charge) + " in file " + options.filename
    print "Please be sure this is correct."
    mol.write(' Charge='+str(charge)+'\n')

for j in range(fact):
    if all[j][2]>0:
        mol.write('        Charge='+all[j][3]+'   Atoms='+str(all[j][2])+'\n')
        mol.write(all[j][1])

mol.close()

