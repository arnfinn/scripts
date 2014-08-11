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

def derive(f,h):
    if len(f) == 2:
        return two_point_deriv(f[0],f[1],h)
    elif len(f) == 4:
        return five_point_stencil(f[0],f[1],f[2],f[3],h)
    else:
        exit("Something wrong with the input to derive routine")

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

def make_NEF_dal(old_dal, h, two=False, dryrun=False, force=False, nef="003"):
    # make four dal-files with different field strength
    # Replace the two lines after .FIELD, otherwise use
    # the original dalton file
    if not dryrun:
        dallines = read_file(old_dal)
        check_dal(dallines)
    all_files = []
    h = float(h)
    if two:
        fields=[h/2.0,-h/2.0]
    else:
        fields=[2*h,h,-h,-2*h]

    num = 0
    for j in fields:
        num += 1
        dalname = "{0}_NEF-{1}_{2}.dal".format(old_dal.split(".")[0],nef,num)
        all_files.append(dalname)
        if os.path.isfile(dalname) and not force:
            continue
        if not dryrun:
            newdal = ""
            prev = "qwerty"
            for k in dallines:
                if prev[0:6]==".FIELD":
                    newdal += "{0}\n".format(j)
                    prev = k
                elif k[0:4]=="NEF ":
                    newdal += "NEF {0}\n".format(nef)
                    prev = k
                else:
                    newdal += "{0}".format(k)
                    prev = k
            write_file(dalname,newdal)
    return all_files

def run_dalton(exc="dalton",dal="input",mol="input",pot="", cores="1", force=False, dryrun=False):
    if pot == "":
        dalout = dal.split(".")[0] + "_" + mol.split(".")[0] + ".out"
    else:
        dalout = dal.split(".")[0] + "_" + mol.split(".")[0] + "_" + pot.split(".")[0] + ".out"
    if not dryrun:
        dalinp = [exc,"-nobackup","-noarch", "-d", "-N", cores, "-o", dalout, dal, mol, pot]
    if not os.path.isfile(dalout) or force:
        try:
            subprocess.call(dalinp)
        except:
            sys.stderr.write('Something wrong running %s\n' % exc)
            sys.exit(-1)
    return dalout

def extract_data(dalton_file):
    dal_lines = read_file(dalton_file)
    for i in dal_lines[-20:]:
        if "@ << A; B, C, D >>  =" in i:
            order = "cubic"
            value = i.split()[-1]
        elif "@ omega B, omega C, QR value :" in i:
            order = "quadratic"
            value = i.split()[-1]
        elif "@ -<< NEF " in i:
            order = "linear"
            value = i.split()[-1]
    try:
        return float(value.replace('D','E'))
    except:
        exit("No data in the dalton output {0}".format(dalton_file))

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
parser.add_argument("--nef", dest="nef", default="003",
                    help="The nuclear coordinate to run NEF on [default: %(default)s]")
parser.add_argument("-N", "--nodes", dest="nodes", default="1",
                    help="number of nodes/cores to run dalton [default: %(default)s]")
parser.add_argument("--two", action="store_true", dest="two", default=False, 
                    help="Finite field with two intead of four points.")
parser.add_argument("--dryrun", action="store_true", dest="dryrun", default=False, 
                    help="Do not run dalton (if files already exists)")
parser.add_argument("--force", action="store_true", dest="force", default=False, 
                    help="Run dalton even if tensor files already exists")
parser.add_argument("--trash", dest="trash", default=False, 
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

new_dal = make_NEF_dal(args.dalfile, args.field, two=args.two, dryrun=args.dryrun, force=args.force, nef=args.nef)

dal_out = []
for i in new_dal:
    dal_out.append(run_dalton(exc=args.execute,dal=i,mol=args.molfile,pot=args.potfile,cores=args.nodes,force=args.force, dryrun = args.dryrun))

out_values = []
for i in dal_out:
    out_values.append(extract_data(i))

derived_value = derive(out_values,args.field)

print derived_value

if args.potfile:
    outfile ="{0}_{1}_{2}.finite_field_output".format(args.dalfile.split(".")[0], args.molfile.split(".")[0], args.potfile.split(".")[0])
else:
    outfile ="{0}_{1}.finite_field_output".format(args.dalfile.split(".")[0], args.molfile.split(".")[0])

write_file(outfile,"{0}\n".format(derived_value))


if args.trash:
    for i in new_dal:
        if args.trash == "all":
            out = "{0}_{1}.out".format(i.split(".")[0], args.molfile.split(".")[0])
            try:
                # if it has already been removed in a previous run
                os.remove(out)
            except:
                pass
        os.remove(i)
            


