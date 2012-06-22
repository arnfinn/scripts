#!/usr/bin/python
# Arnfinn Hykkerud Steindal, Odense Dec. 2009
# Get the excitation energies from
# an output-file

import re
import sys
import shutil
import string

import math
try:
    from scipy.constants import *
    bohr=1e2*physical_constants['Bohr radius'][0]
    eV2au=physical_constants['electron volt-hartree relationship'][0]
    c=c*100
except:
    bohr=5.291772108e-9     # cm
    alpha=0.007297352568    # -
    c=2.99792458e10         # cm/s
    eV2au=0.03674932379     # au/eV
    pi=math.pi              # -

def get_opa_ex(file,line):
# Input:
# 1. Dalton input file
# 2. line "@ Excited state no: ..."
# Output: a (b)
# a = Excitation energy
# b = dipole moment (zero if no diplen keyword)
    excit = ''
    words = line.split()
    for k in range(4):
        line = file.readline()
    words = line.split()
    value = str(float(words[1])+0.0005)
#    value = str(float(words[1])+0.005)
#    value = str(float(words[1]))
    excit = excit + ' ' + value[0:5]
    for k in range(4):
        line = file.readline()
    intens = 0.0
    for k in range(3):
        for j in range(3):
            line = file.readline()
        words = line.split()
        try:
            intens = intens + float(words[5])
        except:
            break
#    intens = intens/3.0
    strint = str(intens)
    if intens<0.001:
        strint = '0.00000'
    excit = excit + ' (' + strint[0:5] + ')'
    return excit

def get_tpa_ex(file,line):
    words = line.split()
    exi_eV = float(words[2])
    sigma_au=float(words[6])
    sigma_GM="%.2f" % au2GM(exi_eV,sigma_au)
    excit = ' ' + words[2] + ' (' + str(sigma_GM) + ')'
    return excit

def au2GM(exi_ev,sigma_au):
    lorentzian=0.0036749326 # au
    const=1e50*8*(pi**2)*alpha*(bohr**5)/(c*lorentzian)
    exi_au=exi_ev*eV2au
    sigma_GM=const*exi_au**2*sigma_au
    return sigma_GM

for i in sys.argv[1:]:
    try:
        file = open(i,'r')
    except:
        print 'Did not find file '+i
        break
    lines = file.readlines()
    a = len(lines)
    file.seek(0)
    prline = ''
    convergence = False
    opa = False
    tpa = False
    threepa = False
    for j in range(a):
        try:
            line = file.readline()
        except:
            break
        words = line.split()
        leng = len(words)
        if leng==7:
            if words[1]=='THE' and  words[2]=='REQUESTED' and  words[6]=='CONVERGED':
                convergence = True
        if convergence:
            if leng==8:
                if words[1]=='Excited' and  words[2]=='state' and words[3]=='no:':
                    opa = True
                    prline = prline + get_opa_ex(file,line)
            if leng==9:
                # 2pa
                if words[3]=='Linear':
                    tpa = True
                    prline = prline + get_tpa_ex(file,line)
            if leng==8:
                # threepa
                if words[3]=='Linear':
                    threepa = True
                    prline = prline + get_tpa_ex(file,line)
    pa = ''
    if threepa:
        pa = '3pa'
    if tpa:
        pa = 'tpa'
    if opa:
        pa = 'opa'

    if prline != '':
        prline = prline + ' ' + pa + ' ' + i
#        out = open('test.out','a')
#        out.write(prline + '\n')
        print prline
#        out.close()
    file.close()
