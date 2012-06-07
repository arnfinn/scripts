#!/usr/bin/env python

#Usage: xyz2molcas.py xyzfile outfile natoms2 charge [a|b]

#Usage: xyz2molcas.py xyzfile outfile
#       (charge as second line in xyzfile)

import sys
NEL={'h':1, 'c':6,'n':7,'o':8,'f':9,'p':15,'s':16,'cl':17,'br':35}

f=open(sys.argv[1]).readlines()
of=open(sys.argv[2],'w')
m1=True
m2=True
if(len(sys.argv)>3):
    n2=int(sys.argv[3])
    charge=int(sys.argv[4])
    try:
        if(sys.argv[5]=='a'): m2=False
        if(sys.argv[5]=='b'): m1=False
    except:
        pass
else:
    n2=0
    try:
        charge=int(f[1])
    except:
        charge=0
    
n=int(f[0])
n1=n-n2
coord=[(x.split()[0], [float(y)/0.529177 for y in x.split()[1:4]]) for x in f[2:2+n]]

def INFO(v):
    if v:
        return "REAL"
    else:
        return "GHOST"

if(n2>0):
    print "Monomer A, ", n1, " atoms, ", INFO(m1)
    print "Monomer B, ", n2, " atoms, ", INFO(m2)

of.write("&Seward &End\nMULTipoles\n3\nCHOINPUT\nThrCon\n1.0E-4\nEndCh\nCHOL\n")
nel=-charge

for i in range(n):
    of.write("Basis set\n%s.A-6-31PGP.....\n%s%03d %20.10f%20.10f%20.10f\n" % ((coord[i][0],coord[i][0],i+1)+tuple(coord[i][1])))
    if(((not m1) and i<n1) or ((not m2) and i>=n1)):
        of.write("Charge\n0.0\n")
    else:
        nel+=NEL[coord[i][0].lower()]
    of.write("End of Basis set\n")
if(nel%2==1): print "WARNING!!! NOT CLOSED SHELL!!! REMOVING AN ELECTRON."
of.write("End of Input\n\n")

#Here we may put in extra commands
#of.write("""
#!cp $HomeDir/$Project.ScfOrb0 $WorkDir/$Project.ScfOrb\n
#""")

of.write("&SCF &END\nKSDFT\nB3LYP\nChoInput\nLOCK\nEndCh\nOCCU\n"+str(nel/2)+"\nEnd of Input\n\n&LOPROP &END\nBonds\n0.0\nEnd of Input\n>>COPY $WorkDir/$Project.MpProp $HomeDir\n")

###
