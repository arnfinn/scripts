#!/usr/bin/python
# Arnfinn Hykkerud Steindal, Tromso Apr 2010; May 2012
# Read a file (-i FILENAME) and make an average of
# values in the first row (if not given as -r ROW).

import sys
import math
from optparse import OptionParser
import re

parser = OptionParser()
parser.add_option("-i", "--input",dest="filename", help="the file to read")
parser.add_option("-r", "--row",type="int", dest="row",  default=1, help="The row where numbers are located")
parser.add_option("-d", "--decimals",type="int", dest="dec", default=4, help="Number of decimals in the printet numbers")
parser.add_option("-p", "--print",action="store_true", default=False, dest="printing", help="Print all the values")
(options, args) = parser.parse_args()
file = open(options.filename,'r')
row = options.row-1
dec = str(options.dec)

lines = file.readlines()
num = 0.0
tall = 0.0
tab=[]

for line in lines:
    words = line.split()
    num = num + 1.0
    ettall = words[row]
    if "." in ettall:
        ettall = float(re.sub("\D","",words[row].split(".")[0])+"."+re.sub("\D","",words[row].split(".")[1]))
    else:
        ettall = float(re.sub("\D","",words[row]))
    if options.printing:
        print ettall
    tall = tall + float(ettall)
    tab.append(ettall)

ave = tall/num
stan=0.0
for i in tab:
    stan=stan+(i-ave)*(i-ave)

stan=math.sqrt(stan/(num-1))

print "Number of values = "+str(int(num))
string = "Average value = %."+dec+"f"
print string % (ave)
string = "Standard deviation = %."+dec+"f"
print string % (stan)
