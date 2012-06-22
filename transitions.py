#!/usr/bin/python
#Arnfinn Hykkerud Steindal, Tromso July 2011
#Get the excitation energies and transitions from an Dalton
#output-file

import re
import sys
import shutil
import string
from mymodules import *

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
#                    print words[4] + ' ' + get_opa_ex(file,line)
                    opa=get_opa_ex(file,line).split('(')
                    printline=words[4] + ' & ' + opa[0] + ' & ' + opa[1][0:5]+'& & '
                    
                    for i in range(8):
                        file.readline()
                    for i in range(100):
                        line=file.readline()
                        words=line.split()
                        try:
                            int(words[0])
                        except:
                            a=len(printline)
                            print printline[0:a-1]
                            break
                        low=int(words[1].split('(')[0])
                        high=int(words[2].split('(')[0])
                        if high-low==1:
                            reduce=low
#                        else:
#                            reduce=127
                            #                        down=str(low-91)
                            #                        up=str(high-92)
                        down=str(low-reduce)
                        up=str(high-reduce-1)
                        if down=='0':
                            mo1='H'
                        else:
                            mo1='H'+down
                        if up=='0':
                            mo2='L'
                        else:
                            mo2='L+'+up
                        percent=100.0*float(words[3])**2+0.5
                        if percent>=5.0:
                            printline=printline+str(percent).split('.')[0]+'\%('+mo1+'$\\to$'+mo2+')+'
#                            print str(percent).split('.')[0]+'\%('+mo1+'$\\to$'+mo2+')'

    file.close()
