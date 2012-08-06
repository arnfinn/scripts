#!/usr/bin/python
# Arnfinn Hykkerud Steindal, Tromso Apr 2010; May 2012
# Read a file (-i FILENAME) and make an average of
# values in the first row (if not given as -r ROW).

import sys
import math
from optparse import OptionParser

def au2ang(value):
    new_value = value*0.529177249
    return new_value


parser = OptionParser()
parser.add_option("-i", "--input",dest="filename", help="the file to read")
(options, args) = parser.parse_args()

file = open(options.filename,'r')
lines = file.readlines()
file.close()

b= len(options.filename)
newfile = open(options.filename[0:b-4]+"_ang.xyz","w")
newfile.write(lines[0]+lines[1])


newlines=""
for line in lines[2:]:
    words = line.split()
    try:
        x=au2ang(float(words[1]))
        y=au2ang(float(words[2]))
        z=au2ang(float(words[3]))
    except:
        break
    newfile.write(line.replace(words[1],str(x)).replace(words[2],str(y)).replace(words[3],str(z)))

newfile.close()    
