#!/bin/bash

#for i in {1..50}; do structures.py -i $1_$i-chrom.pdb; done >$1

# ALL
if grep -q "CD2 - CG2 dis" $1; then
grep "CD2 - CG2 dis" $1>test 
echo "CD2 - CG2 dis"
aver_general.py -i test -r 5
fi

#CFP
if grep -q "CE3 - CD2 dis" $1; then
grep "CE3 - CD2 dis" $1 >test
echo "CE3 - CD2 dis"
aver_general.py -i test -r 5
fi
if grep -q "CZ3 - CE3 dis" $1; then
grep "CZ3 - CE3 dis" $1 >test
echo "CZ3 - CE3 dis"
aver_general.py -i test -r 5
fi
if grep -q "CH2 - CZ3 dis" $1; then
grep "CH2 - CZ3 dis" $1 >test
echo "CH2 - CZ3 dis"
aver_general.py -i test -r 5
fi
if grep -q "CH2 - CZ2 dis" $1; then
grep "CH2 - CZ2 dis" $1 >test
echo "CH2 - CZ2 dis"
aver_general.py -i test -r 5
fi
if grep -q "CZ2 - CE2 dis" $1; then
grep "CZ2 - CE2 dis" $1 >test
echo "CZ2 - CE2 dis"
aver_general.py -i test -r 5
fi
if grep -q "CE2 - CD2 dis" $1; then
grep "CE2 - CD2 dis" $1 >test
echo "CE2 - CD2 dis"
aver_general.py -i test -r 5
fi
if grep -q "CE2 - NE1 dis" $1; then
grep "CE2 - NE1 dis" $1 >test
echo "CE2 - NE1 dis"
aver_general.py -i test -r 5
fi
if grep -q "NE1 - CD1 dis" $1; then
grep "NE1 - CD1 dis" $1 >test
echo "NE1 - CD1 dis"
aver_general.py -i test -r 5
fi

#GFP
#if grep -q "CE2 - CD2 dis" $1; then
#grep "CE2 - CD2 dis" $1 >test
#echo "CE2 - CD2 dis"
#aver_general.py -i test -r 5
#fi
if grep -q "CZ - CE2 dis" $1; then
grep "CZ - CE2 dis" $1 >test
echo "CZ - CE2 dis"
aver_general.py -i test -r 5
fi
if grep -q "OH - CZ dis"  $1; then
grep "OH - CZ dis"  $1 >test
echo "OH - CZ dis"
aver_general.py -i test -r 5
fi
if grep -q "CZ - CE1 dis" $1; then
grep "CZ - CE1 dis" $1 >test
echo "CZ - CE1 dis"
aver_general.py -i test -r 5
fi
if grep -q "CE1 - CD1 dis" $1; then
grep "CE1 - CD1 dis" $1 >test
echo "CE1 - CD1 dis"
aver_general.py -i test -r 5
fi

#BFP
if grep -q "NE2 - CD2 dis" $1; then
grep "NE2 - CD2 dis" $1>test
echo "NE2 - CD2 dis"
aver_general.py -i test -r 5
fi
if grep -q "NE2 - CE1 dis" $1; then
grep "NE2 - CE1 dis" $1 >test
echo "NE2 - CE1 dis"
aver_general.py -i test -r 5
fi
if grep -q "CE1 - ND1 dis" $1; then
grep "CE1 - ND1 dis" $1>test
echo "CE1 - ND1 dis"
aver_general.py -i test -r 5
fi
if grep -q "ND1 - CG2 dis" $1; then
grep "ND1 - CG2 dis" $1>test
echo "ND1 - CG2 dis"
aver_general.py -i test -r 5
fi

#ALL
if grep -q "CD1 - CG2 dis" $1; then
grep "CD1 - CG2 dis" $1 >test
echo "CD1 - CG2 dis"
aver_general.py -i test -r 5
fi
if grep -q "CG2 - CB2 dis" $1; then
grep "CG2 - CB2 dis" $1>test
echo "CG2 - CB2 dis"
aver_general.py -i test -r 5
fi
if grep -q "CB2 - CA2 dis" $1; then
grep "CB2 - CA2 dis" $1>test
echo "CB2 - CA2 dis"
aver_general.py -i test -r 5
fi
if grep -q "CA2 - N2 dis" $1; then
grep "CA2 - N2 dis" $1>test
echo "CA2 - N2 dis" 
aver_general.py -i test -r 5
fi
if grep -q "N2 - C1 dis" $1; then
grep "N2 - C1 dis" $1>test
echo "N2 - C1 dis"
aver_general.py -i test -r 5
fi
if grep -q "C1 - N3 dis" $1; then
grep "C1 - N3 dis" $1 >test
echo "C1 - N3 dis"
aver_general.py -i test -r 5
fi
if grep -q "N3 - C2 dis" $1; then
grep "N3 - C2 dis" $1 >test
echo "N3 - C2 dis"
aver_general.py -i test -r 5
fi
if grep -q "C2 - O2 dis" $1; then
grep "C2 - O2 dis" $1 >test
echo "C2 - O2 dis"
aver_general.py -i test -r 5
fi
if grep -q "C2 - CA2 dis" $1; then
grep "C2 - CA2 dis" $1 >test
echo "C2 - CA2 dis"
aver_general.py -i test -r 5
fi

if grep -q "C1 - CA1 dis" $1; then
grep "C1 - CA1 dis" $1 >test
echo "C1 - CA1 dis"
aver_general.py -i test -r 5
fi
if grep -q "N3 - CA3 dis" $1; then
grep "N3 - CA3 dis" $1 >test
echo "N3 - CA3 dis"
aver_general.py -i test -r 5
fi

if grep -q "CD1 - CG2 - CB2 angle " $1; then
grep  "CD1 - CG2 - CB2 angle " $1 >test;    echo "CD1 - CG2 - CB2 angle " 
aver_general.py -i test -r 7 --deg
fi
if grep -q "ND1 - CG2 - CB2 angle " $1; then
grep  "ND1 - CG2 - CB2 angle " $1 >test;    echo "ND1 - CG2 - CB2 angle " 
aver_general.py -i test -r 7 --deg
fi
if grep -q "CD2 - CG2 - CB2 angle " $1; then
grep  "CD2 - CG2 - CB2 angle " $1 >test;    echo "CD2 - CG2 - CB2 angle " 
aver_general.py -i test -r 7 --deg
fi
if grep -q "CG2 - CB2 - CA2 angle " $1; then
grep  "CG2 - CB2 - CA2 angle " $1 >test;    echo "CG2 - CB2 - CA2 angle " 
aver_general.py -i test -r 7 --deg
fi
if grep -q "CB2 - CA2 - C2 angle "  $1; then
grep  "CB2 - CA2 - C2 angle "  $1 >test;    echo "CB2 - CA2 - C2 angle "  
aver_general.py -i test -r 7 --deg
fi
if grep -q "CB2 - CA2 - N2 angle "  $1; then
grep  "CB2 - CA2 - N2 angle "  $1 >test;    echo "CB2 - CA2 - N2 angle "    
aver_general.py -i test -r 7 --deg
fi
if grep -q "CD1 CG2 CB2 CA2 dihedral " $1; then
grep  "CD1 CG2 CB2 CA2 dihedral " $1 >test; echo "CD1 CG2 CB2 CA2 dihedral "
aver_general.py -i test -r 6 --deg
fi
if grep -q "ND1 CG2 CB2 CA2 dihedral " $1; then
grep  "ND1 CG2 CB2 CA2 dihedral " $1 >test; echo "ND1 CG2 CB2 CA2 dihedral "
aver_general.py -i test -r 6 --deg
fi
if grep -q "CD2 CG2 CB2 CA2 dihedral " $1; then
grep  "CD2 CG2 CB2 CA2 dihedral " $1 >test; echo "CD2 CG2 CB2 CA2 dihedral "
aver_general.py -i test -r 6 --deg
fi
if grep -q "CG2 CB2 CA2 N2 dihedral "  $1; then
grep  "CG2 CB2 CA2 N2 dihedral "  $1 >test; echo "CG2 CB2 CA2 N2 dihedral " 
aver_general.py -i test -r 6 --deg
fi
if grep -q "CG2 CB2 CA2 C2 dihedral " $1; then
grep  "CG2 CB2 CA2 C2 dihedral "  $1 >test; echo "CG2 CB2 CA2 C2 dihedral " 
aver_general.py -i test -r 6 --deg
fi