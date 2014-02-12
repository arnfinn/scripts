#!/usr/bin/env python
# Arnfinn Hykkerud Steindal, Tromso Feb. 2014
# Compare two tensor files
# and print mean square error
# Copyright: "I do not care"


import math
from argparse import ArgumentParser

def square_diff(t1, t2):
    t1 = float(t1)
    t2 = float(t2)
    return (t1-t2)*(t1-t2)

def percent_diff(t1,t2):
    t1 = float(t1)
    t2 = float(t2)
    return math.fabs(100*(t1-t2)/t1)
    
def check_inp(lines1,lines2):
    # Check if input files is compatible
    k1=0
    k2=0
    for i in lines1:
        words = i.split()
        if len(words) == 3:
            k1 +=1
    for i in lines2:
        words = i.split()
        if len(words) == 3:
            k2 +=1
    if k1 != k2:
        print "Input files not compatible"
        print "{0} numbers in file 1".format(k1*3)
        print "{0} numbers in file 2".format(k2*3)
        quit("Input files not compatible")

def read_file(file):
    tmpfile = open(file,"r")
    lines = tmpfile.readlines()
    tmpfile.close()
    return lines

def write_file(file,content):
    tmpfile = open(file,"w")
    tmpfile.write(content)
    tmpfile.close()


parser = ArgumentParser(description="Compare numbers in two tensor files")

parser.add_argument("-i", "--input",dest="input", nargs=2, required=True,
                    help="The field strength [default: %(default)s]")
parser.add_argument("-p", action="store_true", dest="percent", default=False, 
                    help="Average percentage difference")
parser.add_argument("-v", action="store_true", dest="verbose", default=False, 
                    help="Print more")
args = parser.parse_args()


if args.verbose:
    sys.stdout.write("""
    This is a script\n
    """
                 )

lines1 = read_file(args.input[0])
lines2 = read_file(args.input[1])

check_inp(lines1,lines2)

a = min(len(lines1),len(lines2))

SE = 0.0
k = 0.0
for i in range(a):
    words1 = lines1[i].split()
    words2 = lines2[i].split()
    if len(words1) == 3 and len(words2) == 3:
        for j in range(3):
            if args.percent:
                SE += percent_diff(words1[j],words2[j])
            else:
                SE += square_diff(words1[j],words2[j])
            k += 1.0

MSE = SE/k

print "%.2f" % MSE
