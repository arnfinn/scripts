#!/usr/bin/env python
# Arnfinn Hykkerud Steindal, Tromso Feb. 2014
# Return a value from a tensor (beta and gamma)
# Copyright: "I do not care"


import math
from argparse import ArgumentParser
import sys
import numpy as np
#from numpy import array

def read_file(file):
    tmpfile = open(file,"r")
    lines = tmpfile.readlines()
    tmpfile.close()
    return lines

def write_file(file,content):
    tmpfile = open(file,"w")
    tmpfile.write(content)
    tmpfile.close()


parser = ArgumentParser(description="My potential file manipulation script")

parser.add_argument("-i", "--input",dest="input", required=True,
                    help="Input file")
parser.add_argument("--beta",dest="beta", default="iso",
                    help="Which beta (iso, x, y or z) [default: %(default)s]")
parser.add_argument("-v", action="store_true", dest="verbose", default=False, 
                    help="Print more")
args = parser.parse_args()


if args.verbose:
    sys.stdout.write("""
    This is a script\n
    """
                 )

tensor=read_file(args.input)
tensor_array = []
for i in tensor:
    words = i.split()
    try:
        a=float(words[0])
        b=float(words[1])
        c=float(words[2])
        tensor_array += [a,b,c]
    except:
        pass

alpha, beta, gamma, delta = False, False, False, False
if len(tensor_array) == 9:
    alpha = True
elif len(tensor_array) == 27:
    beta = True
elif len(tensor_array) == 81:
    gamma = True
elif len(tensor_array) == 243:
    delta = True
else:
    quit("Something wrong with input file {0}.\n\
Number of elements in the tensor ({1}) not equal 9, 27, 81 or 243".format(args.input,len(tensor_array)))

if args.verbose:
    print "alpha: {0}; beta: {1}; gamma: {2}; delta: {3}".format(alpha, beta, gamma, delta)
    
#print tensor_array

print_value = 0.0
x_elem = [[0],[4,8,10,12,20,24]]
y_elem = [[13],[1,3,9,17,23,25]]
z_elem = [[26],[2,6,14,16,18,22]]


if alpha:
    high_elem = []
    all_elem = [0, 4, 8]
    div = 3.0
elif beta:
    if args.beta == "iso":
        high_elem = x_elem[0] + y_elem[0] + z_elem[0]
        all_elem = x_elem[1] + y_elem[1] + z_elem[1]
        div = 15.0
    elif args.beta == "x":
        high_elem = x_elem[0]
        all_elem = x_elem[1]
        div = 5.0
    elif args.beta == "y":
        high_elem = y_elem[0]
        all_elem = y_elem[1]
        div = 5.0
    elif args.beta == "y":
        high_elem = y_elem[0]
        all_elem = y_elem[1]
        div = 5.0
    else:
        quit("beta input not correct! Possible values iso, x y z NOT {0}".format(args.coord))
    high_count = 3.0

elif gamma:
    high_elem = [x_elem[0][0],27+y_elem[0][0],27+27+z_elem[0][0]]
    x = np.array(x_elem[1])
    y = 27 + np.array(y_elem[1])
    z = 27 + 27 + np.array(z_elem[1])
    x = x.tolist()
    y = y.tolist()
    z = z.tolist()
    all_elem = x + y + z
    div = 15.0
    high_count = 3.0

elif delta:
    # sum_i sum_j sum_k (ijjkk + ijkjk + ijkkj +
    #                    jijkk + jikjk + jikkj +
    #                    jjikk + jkijk + jkikj +
    #                    jjkik + jkjik + jkkij +
    #                    jjkki + jkjki + jkkji)

    a = np.array([0,1,2,3,4,6,8])
    b = np.array([0,1,3,4,5,7,8])
    c = np.array([0,2,4,5,6,7,8])
    d = np.array([1,2,3,5,6,7])
    abc = [a,b,c]
    bad = [b,a,d]
    cda = [c,d,a]
    dcb = [d,c,b]

    mylist = abc + bad + cda + bad + abc + dcb + cda + dcb + abc

    num = 0
    all_elem = []
    for i in mylist:
        tmp = i + 9*num 
        all_elem += tmp.tolist()
        num += 1

    # xxxxx, yyyyy and zzzzz has to be "counted" nine times
    high_elem = [0,121,242]
    high_count = 8.0
    div = 225.0

for i in all_elem:
    print_value += tensor_array[i]
for i in high_elem:
    print_value += high_count*tensor_array[i]

print_value = print_value/div


if args.verbose:
    if alpha:
        a = "alpha"
    elif beta:
        a = "beta"
    elif gamma:
        a = "gamma"
    elif delta:
        a = "delta"
    print "{0} for input tensor {1} is {2}".format(a,args.input,print_value)

else:
    print print_value
         
