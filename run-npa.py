#!/usr/bin/env python
# Arnfinn Hykkerud Steindal Oct 2014
# Script for running nPA calculations
# with openRSP

from argparse import ArgumentParser
import sys
import time
from os.path import expanduser
import getpass
import subprocess
import os.path
import os

def write_file(filename, content):
    if os.path.isfile(filename):
        print "The file {0} already exist!".format(filename)
        print "It will therefore not be made."
        return
    tmp_file = open(filename, "w")
    tmp_file.write(content)
    tmp_file.close()

def run_dalton(exc="dalton",dal="input",mol="input",pot="", cores="1", force=False):
    if not pot:
        pot = ""
    if pot == "":
    	pre_name = dal.split(".")[0] + "_" + mol.split(".")[0]
    else:
        pre_name = dal.split(".")[0] + "_" + mol.split(".")[0] + "_" + pot.split(".")[0]
    rsp_tensor =  pre_name + ".rsp_tensor_human"
    dalout = pre_name + ".out"
    std_out= open(pre_name + ".stdout", "w")
    dalinp = [exc,"-get", "rsp_tensor_human","-nobackup","-noarch", "-d", "-N", str(cores), "-o", dalout, dal, mol, pot]
    print dalinp
    if not os.path.isfile(rsp_tensor) or force:
    	# only run dalton if rsp tensor is not already there
#        subprocess.call(dalinp)
        subprocess.call(dalinp, stdout=std_out)
#        try:
#        except:
#            sys.stderr.write('Something wrong running %s\n' % exc)
#            sys.exit(-1)
    std_out.close()
    return pre_name

def get_freq(std_out):
    # get the excitation energies calculated by Daniel Frieses openrsp branch
    return 4.0

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
    part_freq = freq/photons
    photons2 = photons + 1
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
'''.format(photons, num, freq)
    for i in range(photons):
        dal_npa += "{0}\n".format(part_freq)
    dal_npa += "*END OF DALTON INPUT\n"
    return dal_npa

user = getpass.getuser()
home = expanduser("~")

parser = ArgumentParser(description="nPA-openrsp run script")
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
parser.add_argument("-s", "--scripts", dest="scripts", default=home+"/bin/npa-scripts/",
					help="The folder containing the npa scripts [default: %(default)s]")
args = parser.parse_args()

start_time = time.time()

# The dalton input file header equal for all calculations
dal_head = make_dal_header(args.xc, args.potfile)

# Get the excitation energies
exc_dal = "exc_num{0}_{1}.dal".format(args.num,args.xc)
write_file(exc_dal, make_dal_exc(dal_head, args.num))

time1 = time.time()
print "Calculating {0} excitation energies".format(args.num)
pre_name = run_dalton(exc=args.dalton, dal=exc_dal, mol=args.molfile, pot=args.potfile, cores=args.mpi)
time2 = time.time()
print "Total time spent on calculating the excitation energies: {0}".format(time2-time1)

freq = get_freq(pre_name+".stdout")

k = 0
# Run npa cross section calculation
for i in freq:
    k += 1
    print "Calculating the {0}pa cross section for frequency number {1} (freq: {2})".format(args.photons, k, i)
    npa_dal = "{0}pa_exc{1}_{2}.dal".format(args.photons, k, args.xc)
    write_file(npa_dal, make_dal_npa(k, args.photons, i))
    time3 = time.time()
    pre_name = run_dalton(exc=args.dalton, dal=npa_dal, mol=args.molfile, pot=args.potfile, cores=args.mpi)
    time4 = time.time()
    print "Time spent on calculating {0}pa for freq {1} (freq: {2})".format(args.photons, k, i)
