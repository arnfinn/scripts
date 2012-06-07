#!/usr/bin/python
# Arnfinn Hykkerud Steindal, Tromso Dec 2011
# Make a xyz file out of a pdb file

import sys

file=open(sys.argv[1]+'.pdb','r')
out=open(sys.argv[1]+'.xyz','w')

lines=file.readlines()
k=0
body=''
for i in lines:
    words=i.split()
    if words[0]=='HETATM' or words[0]=='ATOM':
        ele=words[2][0]
        k=k+1
#        line=ele+str(k)+'   '+words[6]+'   '+words[7]+'   '+words[8]+'\n'
        line=ele+str(k)+'   '+words[5]+'   '+words[6]+'   '+words[7]+'\n'
        body=body+line

out.write(str(k)+'\n\n'+body)
file.close()
out.close()
