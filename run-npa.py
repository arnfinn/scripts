#!/usr/bin/env python
# Arnfinn Hykkerud Steindal Oct 2014
# Script for running nPA calculations
# with the openRSP residue code
# Copyright: "I do not care"

from argparse import ArgumentParser
import sys
import time
from os.path import expanduser
import getpass
import subprocess
import os.path
import os


def sec_to_time(sec):
    hrs = int(sec/3600.0)
    sec -= 3600.0*hrs
    mins = int(sec/60.0)
    sec -= 60.0*mins
    if hrs == 0 and mins == 0:
        return "{0:.4f} sec".format(sec)
    elif hrs == 0:
        return "{1} min {2:.2f} sec".format(hrs, mins, sec)
    else:
        return "{0} h {1} min {2:.2f} sec".format(hrs, mins, sec)

def write_file(filename, content, force=False):
    if os.path.isfile(filename) and not force:
        print "The file {0} already exist!".format(filename)
        print "It will therefore not be made."
        return
    tmpfile = open(filename, "w")
    tmpfile.write(content)
    tmpfile.close()

def read_file(filename):
    tmpfile = open(filename, "r")
    lines = tmpfile.readlines()
    tmpfile.close()
    return lines

def run_dalton(exc="dalton",dal="input",mol="input",pot="", cores="1", force=False):
    if not pot:
        pot = ""
    if pot == "":
    	pre_name = dal.split(".")[0] + "_" + mol.split(".")[0]
    else:
        pre_name = dal.split(".")[0] + "_" + mol.split(".")[0] + "_" + pot.split(".")[0]
    rsp_tensor =  pre_name + ".rsp_tensor_human"
    dalout = pre_name + ".out"
    if not os.path.isfile(pre_name + ".stdout") or force:
        std_out= open(pre_name + ".stdout", "w")
        dalinp = [exc,"-get", "rsp_tensor_human","-nobackup","-noarch", "-d", "-N", str(cores), "-o", dalout, dal, mol, pot]
        subprocess.call(dalinp, stdout=std_out)
        std_out.close()
    return pre_name

def get_freq(std_out):
    # get the excitation energies calculated by Daniel Frieses openrsp branch
    lines = read_file(std_out)
    freq = []
    for i in lines:
        words = i.split()
        try:
            if words[0] == "Energy:":
                freq.append(words[1])
        except:
            pass
    return freq

def get_cs(std_out):
    # get the cross section
    lines = read_file(std_out)
    xrtm = []
    for i in lines:
        if "xrtm=" in i:
            xrtm.append(2*float(i.split()[1]))
    if len(xrtm) == 15:
        return get_4pa_cs(xrtm)
    elif len(xrtm) == 10:
        return get_3pa_cs(xrtm)
    elif len(xrtm) == 6:
        return get_2pa_cs(xrtm)
    else:
        quit("Something wrong! Num ele ({0}) not equal 6 (2pa), 10 (3pa) or 15 (4pa).".format(len(xrtm)))

def get_2pa_cs(xrtm):
    # taken from Daniel Friese and arrange_matrix_2pa
    # Can probably be combined with 3pa, 4pa etc.
    ndim = 3
    matrix=[[0 for x in xrange(ndim)] for x in xrange(ndim)]
    storagelist=[]
    for i in range(ndim):
     for j in range(ndim):
       sortlist=i,j
       if (storagelist.count(sorted(sortlist))==0):
        storagelist.append(sorted(sortlist))
       matrix[i][j]=storagelist.index(sorted(sortlist))
    #Get the two possible contractions for TPA:
    result1=0
    result2=0
    for i in range(ndim):
     for j in range(ndim):
       M1 = xrtm[storagelist.index(sorted([i,j]))]
       M2 = xrtm[storagelist.index(sorted([i,i]))]
       M3 = xrtm[storagelist.index(sorted([j,j]))]
       result1=result1+M1*M1
       result2=result2+M2*M3
    prefac=1.0/15.0
    return prefac * (2 * result1 + result2)

def get_3pa_cs(xrtm):
    # taken from Daniel Friese and arrange_matrix_3pa
    # Can probably be combined with 2pa, 4pa etc.
    ndim = 3
    matrix=[[[0 for x in xrange(ndim)] for x in xrange(ndim)] for x in xrange(ndim)]
    storagelist=[]
    for i in range(ndim):
     for j in range(ndim):
      for k in range(ndim):
       sortlist=i,j,k
       if (storagelist.count(sorted(sortlist))==0):
        storagelist.append(sorted(sortlist))
       matrix[i][j][k]=storagelist.index(sorted(sortlist))
    #Get the two possible contractions for 3PA:
    result1=0
    result2=0
    for i in range(ndim):
     for j in range(ndim):
      for k in range(ndim):
       M1 = xrtm[storagelist.index(sorted([i,j,k]))]
       M2 = xrtm[storagelist.index(sorted([i,i,j]))]
       M3 = xrtm[storagelist.index(sorted([j,k,k]))]
       result1=result1+M1*M1
       result2=result2+M2*M3
    prefac=1.0/35.0
    return prefac * (3 * result2 + 2 * result1)

def get_4pa_cs(xrtm):
    # taken from Daniel Friese and arrange_matrix_4pa
    # Can probably be combined with 2pa, 3pa etc.
    ndim = 3
    storagelist=[]
    for i in range(ndim):
     for j in range(ndim):
      for k in range(ndim):
        for l in range(ndim):
          sortlist=i,j,k,l
          if (storagelist.count(sorted(sortlist))==0):
           storagelist.append(sorted(sortlist))
    #Get the two possible contractions for 4PA:
    result1=0.0
    result2=0.0
    result3=0.0
    for i in range(ndim):
     for j in range(ndim):
      for k in range(ndim):
        for l in range(ndim):
          M1 = xrtm[storagelist.index(sorted([i,i,j,j]))]
          M2 = xrtm[storagelist.index(sorted([k,k,l,l]))]
          M3 = xrtm[storagelist.index(sorted([i,i,j,k]))]
          M4 = xrtm[storagelist.index(sorted([j,k,l,l]))]      
          M5 = xrtm[storagelist.index(sorted([i,j,k,l]))]
          result1=result1+  3.0 * M1*M2
          result2=result2+ 24.0 * M3*M4
          result3=result3+  8.0 * M5*M5
    prefac=1.0/315.0
    return prefac * (result2 + result1 + result3)

def make_dal_header(xc, peqm):
    # make the dalton file header
    dal_head='''**DALTON INPUT
.RUN WAVE
.DIRECT
'''
    if peqm:
        dal_head += '''.PEQM
*PEQM
.DAMP
'''
    dal_head += "**WAVE FUNCTION\n"
    if xc == "HF":
        dal_head += ".HF\n"
    else:
        dal_head += '''.DFT
{0}
'''.format(xc)
    return dal_head

def make_dal_exc(dal_head, num):
    # make the dalton file for calculating the exc. energies
    dal_exc = dal_head + '''**OPENR
.EXCITAT
{0}
.RESIDU
1
.RENPER
2
.RSPECP
1
.RSPCIX
2
.RESRUL
0
1
.RSNSTA
1
.RESSTA
01
*END OF INPUT
'''.format(num)
    return dal_exc

def make_dal_npa(num, photons, freq):
    part_freq = float(freq)/float(photons)
    rspcix = ""
    rsp_count = 2
    for i in range(photons):
        rspcix += "{0} ".format(rsp_count) 
        rsp_count += 1
    dal_npa = dal_head +'''**OPENR
.EXCITAT
{0}
.RESIDU
1
.RENPER
{1}
.RSPECP
{2}
.RSPCIX
'''.format(num, photons + 1, photons)
    dal_npa += "{0}\n".format(rspcix)
    dal_npa += '''.RESRUL
0
{0}
.RSNSTA
1
.RESSTA
{1}
.RESFRQ
{2}
'''.format(photons, num, -float(freq))
    for i in range(photons):
        dal_npa += "{0}\n".format(part_freq)
    dal_npa += "*END OF DALTON INPUT\n"
    return dal_npa

###################################
# This is where the script starts #
###################################

start_time = time.time()

user = getpass.getuser()
home = expanduser("~")

parser = ArgumentParser(description="My (Arnfinns) nPA-openrsp run script.")
parser.add_argument("-n","--num", dest="num", default=2,
					help="Number of excitations [default: %(default)s]")
parser.add_argument("-p","--photons", dest="photons", default=4, type=int,
					help="Number of photons in 'n photon absorption' [default: %(default)s]")
parser.add_argument("-f","--xc",dest="xc", default="CAMB3LYP",
					help="The XC functional [default: %(default)s]")
parser.add_argument("-m", "--mol",dest="molfile", required=True,
                    help="The mol input file")
parser.add_argument("--mpi", dest="mpi", default=20,
					help="Number of cores to run dalton on [default: %(default)s]")
parser.add_argument("--pot",dest="potfile",
                    help="The pot input file (if peqm)")
parser.add_argument("-d","--dalton", dest="dalton", default=home+"/dalton-openrsp/build-openrsp-npa/dalton",
					help="The location of the dalton script [default: %(default)s]")
parser.add_argument("--skip", dest="skip", default = False, action="store_true",
                    help = "Skip the actual calculation if the std.out files are already there")
parser.add_argument("-v", "--verbose", dest="verbose", default = False, action="store_true",
                    help = "Print more")
args = parser.parse_args()

# The dalton input file header equal for all calculations
dal_head = make_dal_header(args.xc, args.potfile)

if args.skip:
    force = False
else:
    force = True
if args.photons not in [2,3,4]:
    quit("ERROR: {0}pa calculations not 'implemented'!".format(args.photons))

###############################
# Get the excitation energies #
###############################

exc_dal = "exc_num{0}_{1}.dal".format(args.num,args.xc)
write_file(exc_dal, make_dal_exc(dal_head, args.num), force=True)
if args.verbose:
    time1 = time.time()
    print "Calculating {0} excitation energies".format(args.num)
# run the actual calculation
pre_name = run_dalton(exc=args.dalton, dal=exc_dal, mol=args.molfile, pot=args.potfile, cores=args.mpi, force=force)
if args.verbose:
    time2 = time.time()
    print "Total time spent on calculating the excitation energies: {0}".format(sec_to_time(time2-time1))
freq = get_freq(pre_name+".stdout")

#####################################
# Run npa cross section calculation #
#####################################

k = 0
for i in freq:
    k += 1
    if args.verbose:
        time3 = time.time()
        print "Calculating the {0}pa cross section for frequency number {1} (freq: {2})".format(args.photons, k, i)
    npa_dal = "{0}pa_exc{1}_{2}.dal".format(args.photons, k, args.xc)
    write_file(npa_dal, make_dal_npa(k, args.photons, i), force=True)
    # run the actual calculation
    pre_name = run_dalton(exc=args.dalton, dal=npa_dal, mol=args.molfile, pot=args.potfile, cores=args.mpi, force=force)
    if args.verbose:
        time4 = time.time()
        print "Time spent on calculating {0}pa for freq {1}: {2}".format(args.photons, k, sec_to_time(time4-time3))
    cs = get_cs(pre_name+".stdout")
    print '''
Frequency:     {0}
Cross section: {1}
'''.format(i,cs)

if args.verbose:
    final_time = time.time()
    print "Total time spent: {0}".format(sec_to_time(final_time-start_time))
    
