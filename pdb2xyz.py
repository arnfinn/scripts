#!/usr/bin/python
# Arnfinn Hykkerud Steindal, Tromso Dec 2011
# Make a xyz file out of a pdb file

import sys
from argparse import ArgumentParser

parser = ArgumentParser()
parser.add_argument("-i", "--input",dest="filename", help="the file to read")
parser.add_argument("--num", action="store_true", dest="num", default=False, 
                    help="Add numbers to atoms in the xyz file")

args = parser.parse_args()

file = open(args.filename,'r')
a=len(args.filename)
out=open(args.filename[0:a-4]+'.xyz','w')

lines=file.readlines()
k=0
body=''
charge=0
for i in lines:
    if i[0:6]=='HETATM' or i[0:4]=='ATOM':
        k=k+1
        if args.num:
            line=i[77]+str(k)+'   '+i[30:38]+'   '+i[38:46]+'   '+i[46:54]+'\n'
        else:
            line=i[77]+'   '+i[30:38]+'   '+i[38:46]+'   '+i[46:54]+'\n'

        body=body+line
        try:
            if i[79]=="+":
                charge=charge+1
            elif i[79]=="-":
                charge=charge-1
        except:
            charge=charge

#out.write(str(k)+'\n'+str(charge)+'\n'+body)
out.write(str(k)+'\n\n'+body)
file.close()
out.close()
