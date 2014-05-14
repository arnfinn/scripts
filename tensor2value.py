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

def levi_civita(a,b,c):
    xyz_dict = {"x":1,"y":2,"z":3}
    d = xyz_dict[a]
    e = xyz_dict[b]
    f = xyz_dict[c]
    return (d-e)*(e-f)*(f-d)/2

parser = ArgumentParser(description="My potential file manipulation script")

parser.add_argument("-i", "--input",dest="input", required=True,
                    help="Input file")
parser.add_argument("--beta",dest="beta", default="iso",
                    help="Which beta (iso, x, y or z) [default: %(default)s]")
parser.add_argument("--delta",dest="delta", default="iso",
                    help="Which delta (iso, x, y or z) [default: %(default)s]")
parser.add_argument("-v", action="store_true", dest="verbose", default=False, 
                    help="Print more")
args = parser.parse_args()


if args.verbose:
    sys.stdout.write("""
    This is a script for converting tensors to isotropic values
    Arnfinn Hykkerud Steindal, 2014
    Copyright: "I do not care"\n
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
    print " alpha: {0}\n beta:  {1}\n gamma: {2}\n delta: {3}\n\n Total number of tensor elements: {4}\n".format(alpha, beta, gamma, delta, len(tensor_array))
    
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
    ele = ["x","y","z"]
    tensor_ele = []
    for i in ele:
        for j in ele:
            for k in ele:
                for l in ele:
                    for m in ele:
                        tensor_ele.append(i+j+k+l+m) 

    if len(tensor_ele) != len(tensor_array):
        quit("Something wrong! length of tensors not equal")

    if args.delta == "iso":
        ele_one = ele
    else:
        ele_one = args.delta
        if ele_one not in ele:
            quit("delta input not correct! Possible values iso, x y z NOT {0}".format(args.delta))

    for i in range(len(tensor_ele)):
        ijklm = list(tensor_ele[i])
        a = ijklm[0]
        if a not in ele_one:
            continue
        b = ijklm[1]
        c = ijklm[2]
        d = ijklm[3]
        e = ijklm[4]
        if d == e:
            if levi_civita(a,b,c) != 0:
                print_value += levi_civita(a,b,c)*tensor_array[i]
        if c == e:
            if levi_civita(a,b,d) != 0:
                print_value += levi_civita(a,b,d)*tensor_array[i]
        if c == d:
            if levi_civita(a,b,e) != 0:
                print_value += levi_civita(a,b,e)*tensor_array[i]
    div = 30.0

if not delta:
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
    print " {0} for input tensor {1} is\n {2:.8f}".format(a,args.input,print_value)

else:
    print "{0:.8f}".format(print_value)
         
