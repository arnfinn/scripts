#!/usr/bin/env python
# Arnfinn Hykkerud Steindal, Tromso Jan. 2014
# Finite field
# using 5-point stencil
# Copyright: "I do not care"


import math
from argparse import ArgumentParser
import sys
import subprocess
import os.path
import os

def five_point_stencil(f1, f2, f3, f4, h):
    # from wikipedia
    deriv = (-f1+8.0*f2-8.0*f3+f4)/(12.0*h)
    return deriv

def two_point_deriv(f1,f2,h):
    deriv = (f1-f2)/h
    return deriv

def check_dal(dallines):
    # Check if dalton input file is ok
    ok = 0
    for i in dallines:
        if i[0:6] == ".FIELD":
            ok += 1
        if i[0:6] == "*HAMIL":
            ok += 1
    if ok != 2:
        print "Something wrong with the dalton input"
        if ok == 1:
            print ".FIELD or *HAMIL missing"
        elif ok == 0:
            print ".FIELD and *HAMIL missing"
        elif ok > 2:
            print "Several .FIELD (not supported yet)"
        quit("Something wrong with the dalton input")


def make_new_dal(old_dal, h, two=False, dryrun=False):
    # make four dal-files with different field strength
    # Replace the two lines after .FIELD, otherwise use
    # the original dalton file
    if not dryrun:
        dallines = read_file(old_dal)
        check_dal(dallines)
    all_files = []
    h = float(h)
    prev = "rubish"
    if two:
        fields=[h,0.0]
    else:
        fields=[2*h,h,-h,-2*h]

    for i in ["XDIPLEN", "YDIPLEN", "ZDIPLEN"]:
        num = 0
        for j in fields:
            num += 1
            dalname = "{0}_{1}_{2}.dal".format(old_dal.split(".")[0],i,num)
            all_files.append(dalname)
            if os.path.isfile(dalname):
                continue
            if not dryrun:
                newdal = ""
                for k in dallines:
                    if prev[0:6]==".FIELD":
                        newdal += "{0}\n".format(j)
                        prev = "direction"
                    elif prev=="direction":
                        newdal += "{0}\n".format(i)
                        prev = "rubish"
                    else:
                        newdal += "{0}".format(k)
                        prev = k
                tmp_file = open(dalname,"w")
                tmp_file.write(newdal)
                tmp_file.close()
    return all_files

def run_dalton(exc="dalton",dal="input",mol="input",pot="", cores="1", dalton=False, force=False):
    if pot == "":
        rsp_tensor = dal.split(".")[0] + "_" + mol.split(".")[0] + ".rsp_tensor_human"
        dalout = dal.split(".")[0] + "_" + mol.split(".")[0] + ".out"
    else:
        rsp_tensor = dal.split(".")[0] + "_" + mol.split(".")[0] + "_" + pot.split(".")[0] + ".rsp_tensor_human"
        dalout = dal.split(".")[0] + "_" + mol.split(".")[0] + "_" + pot.split(".")[0] + ".out"
    if dalton:
        dalinp = [exc,"-nobackup","-noarch", "-d", "-N", cores, "-o", dalout, dal, mol, pot]
    else:
        dalinp = [exc,"-get", "rsp_tensor_human","-nobackup","-noarch", "-d", "-N", cores, "-o", dalout, dal, mol, pot]

    if not os.path.isfile(rsp_tensor) or force:
        try:
            if not dalton:
                subprocess.call(dalinp)
            elif not os.path.isfile(dalout) or force:
                subprocess.call(dalinp)
        except:
            sys.stderr.write('Something wrong running %s\n' % exc)
            sys.exit(-1)

def dal_to_tensor(tensor_names, force=False):
    for i in tensor_names:
        dalout = i.split(".")[0] + ".out"
        output = read_file(dalout)
        A = ["X;X,X"]
        B = ["Y;X,X"]
        C = ["Z;X,X"]
        D = ["Y;Y,X"]
        E = ["Z;Y,X"]
        F = ["Z;Z,X"]
        G = ["Y;Y,Y"]
        H = ["Z;Y,Y"]
        I = ["Z;Z,Y"]
        J = ["Z;Z,Z"]
        all_ele = [A,B,C,D,E,F,G,H,I,J]
        for j in output:
            try:
                if "B-freq" in j:
                    for k in all_ele:
                        if k[0] in j:
                            words = j.split()
                            k.append(float(words[9]))
            except:
                pass

        beta_tensor = "\n"
        for j in [A,B,C]:
            beta_tensor += "        {0:12.8f}".format(j[1])
        beta_tensor += "\n"
        for j in [B,D,E]:
            beta_tensor += "        {0:12.8f}".format(j[1])
        beta_tensor += "\n"
        for j in [C,E,F]:
            beta_tensor += "        {0:12.8f}".format(j[1])
        beta_tensor += "\n\n"
        for j in [B,D,E]:
            beta_tensor += "        {0:12.8f}".format(j[1])
        beta_tensor += "\n"
        for j in [D,G,H]:
            beta_tensor += "        {0:12.8f}".format(j[1])
        beta_tensor += "\n"
        for j in [E,H,I]:
            beta_tensor += "        {0:12.8f}".format(j[1])
        beta_tensor += "\n\n"
        for j in [C,E,F]:
            beta_tensor += "        {0:12.8f}".format(j[1])
        beta_tensor += "\n"
        for j in [E,H,I]:
            beta_tensor += "        {0:12.8f}".format(j[1])
        beta_tensor += "\n"
        for j in [F,I,J]:
            beta_tensor += "        {0:12.8f}".format(j[1])
        beta_tensor += "\n\n"

        if not os.path.isfile(i) or force:
            write_file(i,beta_tensor)

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

parser.add_argument("-f", "--field",dest="field", type=float, default=0.001,
                    help="The field strength [default: %(default)s]")
parser.add_argument("-d", "--dal",dest="dalfile", required=True,
                    help="The dalton-openrsp input file. Remember .FIELD XX; XX will be replaced by field")
parser.add_argument("-m", "--mol",dest="molfile", required=True,
                    help="The mol input file")
parser.add_argument("-p", "--pot",dest="potfile", default="",
                    help="pot input file")
parser.add_argument("-x", "--executable", dest="execute",
                    help="The (dalton) executable")
parser.add_argument("-N", "--nodes", dest="nodes", default="1",
                    help="number of nodes/cores to run dalton [default: %(default)s]")
parser.add_argument("--dalton", action="store_true", dest="dalton", default=False, 
                    help="Finite field with regular dalton instead of openRSP (only for beta to gamma!).")
parser.add_argument("--two", action="store_true", dest="two", default=False, 
                    help="Finite field with two intead of four points.")
parser.add_argument("--dryrun", action="store_true", dest="dryrun", default=False, 
                    help="Do not run dalton (if files already exists)")
parser.add_argument("--force", action="store_true", dest="force", default=False, 
                    help="Run dalton even if tensor files already exists")
parser.add_argument("--trash", action="store_true", dest="trash", default=False, 
                    help="Remove all the files produced by the script (and dalton)")
parser.add_argument("-v", action="store_true", dest="verbose", default=False, 
                    help="Print more")
args = parser.parse_args()

if not args.execute and not args.dryrun:
    exit("Dalton executable (-x DALTON) not specified!")

if args.verbose:
    sys.stdout.write("""
    This is a script\n
    """
                 )

new_dal = make_new_dal(args.dalfile, args.field, two=args.two, dryrun=args.dryrun)

for i in new_dal:
    if not args.dryrun:
        run_dalton(exc=args.execute,dal=i,mol=args.molfile,pot=args.potfile,cores=args.nodes,dalton=args.dalton,force=args.force)

# The names of the tensor files produced by dalton
tensor_out = []
for i in new_dal:
    if args.potfile:
        tensor_out.append("{0}_{1}_{2}.rsp_tensor_human".format(i.split(".")[0], args.molfile.split(".")[0], args.potfile.split(".")[0]))
    else:
        tensor_out.append("{0}_{1}.rsp_tensor_human".format(i.split(".")[0], args.molfile.split(".")[0]))

if args.dalton:
    dal_to_tensor(tensor_out, force=args.force)

# Read tensor data
tensor_data = []
for i in tensor_out:
    tensor_data.append(read_file(i))

out_tensor = ""
if args.two:
    points = 2
else:
    points = 4

# Use tensor_data to make higher order tensor
for i in range(3): # X Y and Z
    for j in range(len(tensor_data[0])-1): # read all lines, except last, in files
        if len(tensor_data[0]) == 2:
            line = "\n"
        else:
            line = ""
        for k in range(3): # three numbers in a row
            t = []
            for l in range(points):
                filenum = points*i + l
                try:
                    if len(tensor_data[0]) == 2:
                        # dirty fix for "dipole to alpha"
                        t.append(float(tensor_data[filenum][1].split()[k]))
                    else:
                        t.append(float(tensor_data[filenum][j].split()[k]))
                except:
                    break
            if len(t)==points:
                if args.two:
                    deriv = two_point_deriv(t[0],t[1],float(args.field))
                else:
                    deriv = five_point_stencil(t[0],t[1],t[2],t[3],float(args.field))
                mynum = "%.8f" % deriv
                myspace = 20 - len(mynum)
                line += myspace*" "+mynum
        out_tensor += "{0}\n".format(line)
if len(tensor_data[0]) == 2:
    out_tensor += "\n"


if args.verbose:
    print "The higher order tensor\n"
    print out_tensor

if args.potfile:
    outfile ="{0}_{1}_{2}.finite_field_tensor".format(args.dalfile.split(".")[0], args.molfile.split(".")[0], args.potfile.split(".")[0])
else:
    outfile ="{0}_{1}.finite_field_tensor".format(args.dalfile.split(".")[0], args.molfile.split(".")[0])

write_file(outfile,out_tensor)

if args.trash:
    for i in new_dal:
        out = "{0}_{1}.out".format(i.split(".")[0], args.molfile.split(".")[0])
#        tensor = "{0}_{1}.rsp_tensor_human".format(i.split(".")[0], args.molfile.split(".")[0])
        try:
            # if it has already been removed in a previous run
            os.remove(out)
        except:
            pass
        os.remove(i)


