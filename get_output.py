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

def get_property(lines):
    lrsp = False
    qrsp = False
    crsp = False
    rsp = False
    prop = ""
    for i in lines[150:250]:
        try:
            dalinp = i[0:7]
        except:
            continue
        if dalinp == ".RUN RE":
            rsp = True
        elif dalinp == ".RUN PR":
            prop = "dipole"
            break
        if rsp:
            if dalinp == "*LINEAR":
                lrsp = True
            elif dalinp == "*QUADRA":
                qrsp = True
            elif dalinp == "*CUBIC ":
                crsp = True
        if lrsp:
            if dalinp == ".SINGLE":
                prop = "1pa"
                break
            elif dalinp == ".DIPLEN":
                prop = "alpha"
        elif qrsp:
            if dalinp == ".TWO-PH":
                prop = "2pa"
                break
            elif dalinp == ".DIPLEN":
                prop = "beta"
        elif crsp:
            if dalinp == ".DIPLEN":
                prop = "gamma"
                break
    if rsp:
        convergence = False
        for i in lines:
            words = i.split()
            try:
                if words[1]=='THE' and  words[2]=='REQUESTED' and  words[6]=='CONVERGED':
                    convergence = True
            except:
                pass
        if not convergence:
            exit("Response calculation did not converge")
    return prop

def get_output(lines,prop):
    if prop == "1pa":
        output = get_opa(lines)
    elif prop =="2pa":
        output = get_tpa(lines)
    elif prop == "alpha":
        output = get_alpha(lines)
    elif prop == "beta":
        output = get_beta(lines)
    elif prop == "gamma":
        output = get_gamma(lines)
    elif prop == "dipole":
        output = get_dipole(lines)
    else:
        output = ""
    return output

def get_dipole(lines):
    count = False
    k = -999
    for i in lines:
        if "Dipole moment" in i:
            count = True
            k = 0
        if count:
            k+=1
        if k == 5:
            return i.split()[0]

def get_opa(lines):
    read_exc = False
    exc = []
    osc = []
    opa_string = ""
    for i in lines:
        if "@ Excitation energy :" in i:
            read_exc = True
            osc_tmp = 0.0
            k = 0
        elif read_exc:
            exc.append(i.split()[1])
            read_exc = False
        if "@ Oscillator strength (LENGTH)" in i:
            osc_tmp += float(i.split()[5])
            k += 1
            if k == 3:
                osc.append(osc_tmp)
    if len(osc) != len(exc):
        print osc, exc
        exit("Something wrong in get_opa!")
    for i in range(len(osc)):
        if osc[i] < 0.0001:
            osc[i] = 0.0000
        opa_string += "{0:.3f} ({1:.3f}) ".format(float(exc[i]),osc[i])
    return opa_string

def get_tpa(lines):
    get_data = False
    tpa_string = ""
    for i in lines:
        if "Two-photon absorption summary" in i:
            get_data = True
            exc = []
            GM = []
        if get_data:
            words = i.split()
            if len(words) == 9:
                if words[3] == "Linear":
                    exc.append(words[2])
                    sigma_au=float(words[6])
                    GM.append(au2GM(float(words[2]),sigma_au))
    if len(exc) != len(GM):
        exit("Something wrong in get_tpa!")
    for i in range(len(exc)):
        tpa_string += "{0:.2f} ({1:.3f}) ".format(float(exc[i]),float(GM[i]))
    return tpa_string

def get_alpha(lines):
    k = 0
    indep = False
    freqd = False
    alpha_freq = ""
    for i in lines:
        if "@ FREQUENCY INDEPENDENT SECOND ORDER PROPERTIES" in i:
            indep = True
            k = 0
        elif "@ FREQUENCY DEPENDENT SECOND ORDER PROPERTIES WITH FREQUENCY :" in i:
            freqd = True
            k = 0
        if indep or freqd:
            k += 1
            if "@ -<< XDIPLEN  ; XDIPLEN  >> =" in i:
                xx = float(i.split()[7].replace('D','E'))
            elif "@ -<< YDIPLEN  ; YDIPLEN  >> =" in i:
                yy = float(i.split()[7].replace('D','E'))
            elif "@ -<< ZDIPLEN  ; ZDIPLEN  >> =" in i:
                zz = float(i.split()[7].replace('D','E'))
            if k == 9:
                if indep:
                    alpha_indep = (xx + yy + zz)/3.0
                    indep = False
            if k == 15:
                alpha_freq = (xx + yy + zz)/3.0
                freqd = False
    return "{0}    {1}".format(alpha_indep, alpha_freq)

def get_beta(lines):
    beta = 0.0
    for i in lines:
        for k in ["X","Y","Z"]:
            for l in ["X","Y","Z"]:
                if "beta("+k+";"+l+","+l+")" in i:
                    if k+l+l in ["YXX","ZXX","ZYY"]:
                        # XXY, XXZ and YZZ not printed to output
                        prefact = 2.0
                    else:
                        prefact = 1.0
                    words = i.split()
                    try:
                        beta += prefact*float(words[9])
                    except:
                        pass
                if "beta("+l+";"+k+","+l+")" in i:
                    words = i.split()
                    try:
                        beta += float(words[9])
                    except:
                        pass
                if "beta("+l+";"+l+","+k+")" in i:
                    if l+l+k in ["YYX","ZZX","ZZY"]:
                        # YXY, ZXZ and ZYZ not printed to output
                        prefact = 2.0
                    else:
                        prefact = 1.0
                    words = i.split()
                    try:
                        beta += prefact*float(words[9])
                    except:
                        pass
    return beta/15.0

def get_gamma(lines):
    for i in lines:
        if "@ Averaged gamma parallel to the applied field is" in i:
            words = i.split()
            return words[-1]


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
    value = str(float(words[1])+0.00005)
#    value = str(float(words[1])+0.005)
#    value = str(float(words[1]))
    excit = excit + ' ' + value[0:6]
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
    const=1e50*8*(pi**2)*alpha*(bohr**5)/(c*lorentzian*4)
    exi_au=exi_ev*eV2au
    sigma_GM=const*exi_au**2*sigma_au
    return sigma_GM

for i in sys.argv[1:]:
    try:
        myfile = open(i,'r')
    except:
        print 'Did not find file '+i
        break
    lines = myfile.readlines()
    myfile.close()

    prop = get_property(lines)
    prline = get_output(lines,prop)

    if prline != '':
        print "{0}  {1}  {2}".format(prline, prop, i)


