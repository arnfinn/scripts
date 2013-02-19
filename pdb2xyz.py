#!/usr/bin/python
# Arnfinn Hykkerud Steindal, Tromso Dec 2011
# Make a xyz file out of a pdb file

import sys
from optparse import OptionParser

parser = OptionParser()
parser.add_option("-i", "--input",dest="filename", help="the file to read")
(options, args) = parser.parse_args()
file = open(options.filename,'r')
a=len(options.filename)
out=open(options.filename[0:a-4]+'.xyz','w')

lines=file.readlines()
k=0
body=''
for i in lines:
    if i[0:6]=='HETATM' or i[0:4]=='ATOM':
        ele=i[13]
        k=k+1
        line=ele+str(k)+'   '+i[32:38]+'   '+i[41:46]+'   '+i[48:54]+'\n'
        body=body+line

out.write(str(k)+'\n\n'+body)
file.close()
out.close()
