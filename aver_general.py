#!/usr/bin/python
# Arnfinn Hykkerud Steindal, Tromso Apr 2010; May 2012
# Read a file (-i FILENAME) and make an average of
# values in the first row (if not given as -r ROW).

import sys
import math
from optparse import OptionParser
import re

def aver(mylist):
    tot = 0.0
    for i in mylist:
        tot=tot+i
    return tot/len(mylist)

def stdev(mylist):
    ave = aver(mylist)
    stan=0.0
    for i in mylist:
        stan=stan+(i-ave)*(i-ave)
    return math.sqrt(stan/(len(mylist)-1))

def ev2nm(mylist):
    newlist=[]
    for i in mylist:
        newlist.append(1240.0/i)
    return newlist

parser = OptionParser()
parser.add_option("-i", "--input",dest="filename", help="the file to read")
parser.add_option("-r", "--row",type="int", dest="row",  default=1, help="The row where numbers are located")
parser.add_option("-d", "--decimals",type="int", dest="dec", default=4, help="Number of decimals in the printet numbers")
parser.add_option("-p", "--print",action="store_true", default=False, dest="printing", help="Print all the values")
parser.add_option("--ev2nm",action="store_true", default=False, dest="ev2nm", help="Convert from eV to nm before calculating average")
parser.add_option("--av2",action="store_true", default=False, dest="aver2", help="Calculate the average of numbers where two are weighted")
parser.add_option("--avnum",type="int", dest="avernum", default=0,help="Calculate the average of the N first values")
(options, args) = parser.parse_args()
file = open(options.filename,'r')
row = options.row-1
dec = str(options.dec)

if options.avernum>0:
    lines = file.readlines()[0:options.avernum]
else:
    lines = file.readlines()
tab=[]

for line in lines:
    words = line.split()
    if options.aver2:
        oneex = float(re.sub("\D","",words[0].split(".")[0])+"."+re.sub("\D","",words[0].split(".")[1]))
        onetr = float(re.sub("\D","",words[1].split(".")[0])+"."+re.sub("\D","",words[1].split(".")[1]))
        twoex = float(re.sub("\D","",words[2].split(".")[0])+"."+re.sub("\D","",words[2].split(".")[1]))
        twotr = float(re.sub("\D","",words[3].split(".")[0])+"."+re.sub("\D","",words[3].split(".")[1]))
        ettall=str((oneex*onetr + twoex*twotr)/(onetr + twotr))
#        print "two "+ettall
    else:
        ettall = words[row]
#        print "one " +ettall
    if "." in ettall:
        ettall = float(re.sub("\D","",ettall.split(".")[0])+"."+re.sub("\D","",ettall.split(".")[1]))
#        ettall = float(re.sub("\D","",words[row].split(".")[0])+"."+re.sub("\D","",words[row].split(".")[1]))
    else:
        ettall = float(re.sub("\D","",ettall))
#        ettall = float(re.sub("\D","",words[row]))
    if options.printing:
        print ettall
    tab.append(ettall)

if options.ev2nm:
    tab = ev2nm(tab)
    
ave = aver(tab)
stan = stdev(tab)

print "Number of values = "+str(len(tab))
string = "Average value = %."+dec+"f"
print string % (ave)
string = "Standard deviation = %."+dec+"f"
print string % (stan)
