#!/usr/bin/python
#Arnfinn Hykkerud Steindal, Tromso July 2011
#Get the excitation energies and transitions from an Dalton
#output-file

import re
import sys
import shutil
import string
from optparse import OptionParser

from mymodules import *


def get_homo(file):
    for i in file.readlines():
        words=i.split()
        leng=len(words)
        if "Orbital occupations :" in i:
            homo = int(words[3])
            break
#        if leng==4:
#            if words[0]=='Orbital' and  words[1]=='occupations' and words[2]==':':
#                homo = int(words[3])
    file.seek(0)
    return homo

def convergence(file):
    conv = False
    for i in file.readlines():
        if "SOLUTION VECTORS CONVERGED" in i and "THE REQUESTED" in i:
            conv = True
            break
    file.seek(0)
    return conv

def get_maxnumtrans(file):
    maxnumtrans = 0
    for i in file.readlines():
        if "SOLUTION VECTORS CONVERGED" in i:
            if "THE REQUESTED" in i:
                words = i.split()
                maxnumtrans = int(words[3])
                break
    file.seek(0)
    return maxnumtrans


parser = OptionParser()
parser.add_option("-i", "--input",dest="filename", help="The input file")
parser.add_option("-l", "--latex",action="store_true",default=False, dest="latex", help="Make LaTeX output")
parser.add_option("-t", "--trans",type="int",default=10, dest="numtrans", help="Maximum number transitions printed")


(options, args) = parser.parse_args()

try:
    file = open(options.filename,'r')
except:
    print 'Did not find file '+i
    exit()

numtrans=options.numtrans
latex=options.latex

maxnum=get_maxnumtrans(file)
if numtrans > maxnum:
    numtrans = get_maxnumtrans(file)

homo=get_homo(file)

prline = ''
convergence = convergence(file)
if not convergence:
    print "The response calculation did not converge"
    exit()

opa = False
tpa = False
threepa = False

numline = len(file.readlines())
file.seek(0)
reader=True

if latex:
    homostr = "H"
    lumostr = "L"
else:
    homostr = "HOMO"
    lumostr = "LUMO"

for i in range(numtrans):
    while reader:
        line = file.readline()
        if "RSPCTL MICROITERATIONS CONVERGED" in line:
            reader = False
    for j in range(50):
        line = file.readline()
        words=line.split()
        leng = len(words)
        if leng==8:
            if words[1]=='Excited' and  words[2]=='state' and words[3]=='no:' and words[4]==str(i+1):
                done=False
                opa = True
                #                    print words[4] + ' ' + get_opa_ex(file,line)
                opa=get_opa_ex(file,line).split('(')
                if latex:
                    printline=words[4] + ' & ' + opa[0] + ' & ' + opa[1][0:5]+'& & '
                else:
                    printline=words[4] + ' ' + opa[0] + 'eV (' + opa[1][0:5]+') -'
                for k in range(8):
                    file.readline()
                for k in range(100):
                    line=file.readline()
                    words=line.split()
                    try:
                        int(words[0])
                    except:
                        a=len(printline)
                        print printline[0:a-1]
                        done=True
                        break
                    low=int(words[1].split('(')[0])
                    high=int(words[2].split('(')[0])
                    down=str(low-homo)
                    up=str(high-homo-1)
                    if down=='0':
                        mo1=homostr
                    else:
                        mo1=homostr+down
                    if up=='0':
                        mo2=lumostr
                    else:
                        mo2=lumostr+"+"+up
                    percent=2*100.0*float(words[3])**2+0.5
                    if percent>=5.0:
                        if latex:
                            printline=printline+str(percent).split('.')[0]+'\%('+mo1+'$\\to$'+mo2+')+'
                        else:
                            printline=printline+" "+str(percent).split('.')[0]+'% ('+mo1+' -> '+mo2+') +'
                if done:
                    break
file.close()
