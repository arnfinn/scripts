#!/usr/bin/env python

from os import path
import argparse as ap

class MpProp2pot:
    def __init__(self,file):
        self.file=file
        try:
            self.finp = open(self.file,"r")
            self.lines=self.finp.readlines()
            self.finp.close()
        except:
            exit('Can not open file {0}. Does it exist?'.format(self.file))

    def get_coor(self):
        k = 9
        for i in range(self.num_atoms()):
            blank = 1
            el = self.lines[k].split()[2][0]
            txt = str(self.get_atomnum(el))

            # coordinates
            k+=1
            txt += self.add_nums(self.lines[k])
            coor = self.add_nums(self.lines[k])


    def pot_lines(self):
        if self.get_pol()!=2:
            exit("Script not implemented for polarization level "
                 "equal to {0} (only 2).".format(self.get_pol()))
        out=[]
        self.mul=self.get_mulpol()
        k=9
        elem = []
        coor = []
        mult = []
        for i in range(self.mul+1):
            mult.append([])
        pol = []

        for i in range(self.num_atoms()):
            blank = 1
            el = self.lines[k].split()[2][0]
            elem.append(el)
            txt = str(self.get_atomnum(el))

            # coordinates
            k+=1
            txt += self.add_nums(self.lines[k])
            coor.append(self.add_nums(self.lines[k]))
            # charge
            k+=1
            txt += self.add_nums(self.lines[k])
            mult[0].append(self.add_nums(self.lines[k]))
            # dipoles
            if self.mul>=1:
                k+=1
                txt += self.add_nums(self.lines[k])
                mult[1].append(self.add_nums(self.lines[k]))
                blank += 1

            # quadropoles
            if self.mul>=2:
                tmp = ""
                for i in range(2):
                    k+=1
                    tmp += self.add_nums(self.lines[k])
                txt += tmp
                mult[2].append(tmp)
                blank += 2

            # octupoles
            if self.mul>=3:
                tmp = ""
                for i in range(4):
                    k+=1
                    tmp += self.add_nums(self.lines[k])
                txt += tmp
                mult[3].append(tmp)

            k = k + blank

            # polarizabilities
            k+=1
            tmp = ""
            for i in range(2):
                tmp += self.add_nums(self.lines[k])
                k+=1
            txt += tmp
            pol.append(tmp)
            out.append(txt)
        return [elem,coor,mult,pol]
#        return out

    def add_nums(self,line):
        num=line.split()
        newline=""
        for i in num:
            a=7-len(i.split(".")[0])
            newline+=a*" "+"%.8f" % float(i)
        return newline

    def filename(self):
        return self.file

    def get_mulpol(self):
        return int(self.lines[6].split()[0])

    def get_pol(self):
        return int(self.lines[6].split()[1])+1

    def num_atoms(self):
        return int(self.lines[8].split()[0])

    def get_atomnum(self,ele):
        self.list={
            "H":1,
            "C":6,
            "N":7,
            "O":8
            }
        try:
            return self.list[ele]
        except:
            exit("Element "+ele+" not in list. Please add it!")


def checkEqual(iterator):
    try:
        iterator = iter(iterator)
        first = next(iterator)
        return all(first == rest for rest in iterator)
    except StopIteration:
        return True

parser = ap.ArgumentParser(description='Molcas MpProp to Dalton pot converter')
parser.add_argument('-i', dest='MpProp', metavar='MpProp_FILE', nargs='+',
                    help='''the name of the MolCas MpProp input files.''')
parser.add_argument('-o', dest='potfile', metavar='POT_FILE',
                    help='''the name of the Dalton pot input file.''')
parser.add_argument('-f', dest='force', action='store_true',
                    default=False,
                    help='''Force overwriting old pot file
                            [default: %(default)s]''')
parser.add_argument('--old', dest='oldpot', action='store_true',
                    default=False,
                    help='''Old pot file format
                            [default: %(default)s]''')
args = parser.parse_args()

if not args.MpProp:
    exit('You must specify at least one .MpProp input file.')
else:
    MpProp = args.MpProp

if not args.potfile:
    # if no pot-file given, name it as the first MpProp-file
    if MpProp[0].endswith('.MpProp'):
        potfile = MpProp[0][0:-7]+".pot"
    else:
        potfile = MpProp[0]+'.pot'
else:
    if args.potfile.endswith('.pot'):
        potfile = args.potfile
    else:
        potfile = args.potfile+".pot"

if path.isfile('{0}'.format(potfile)) and not args.force:
    exit('{0} does already exist. Please run script with -f'
         ' to force overwriting it.'.format(potfile))

totatom = 0
mulpollist=[]
polarilist=[]
textlist = []

for i in MpProp:
    if i.endswith('.MpProp'):
        file = i
    else:
        file = i+'.MpProp'
    if not path.isfile('{0}'.format(file)):
        exit('{0} not found.'.format(file))

    k = MpProp2pot(file)

    mulpollist.append(k.get_mulpol())
    polarilist.append(k.get_pol())
    totatom += k.num_atoms()
    textlist.append(k.pot_lines())


if not checkEqual(mulpollist):
    print("Your MpProp input files have not the same multipole orders")
    print("The mulpol orders are {0} and {1} for the files\n"
          "{2} and {3} respectively".format(
            ', '.join(str(i) for i in mulpollist[:-1]),
            str(mulpollist[-1]),', '.join(str(i) for i in MpProp[:-1]), 
            str(MpProp[-1])))
    exit()
if not checkEqual(polarilist):
    print("Your MpProp input files have not the same multipole orders")
    print("The mulpol orders are {0} and {1} for the files\n"
          "{2} and {3} respectively".format(
            ', '.join(str(i) for i in mulpollist[:-1]),
            str(mulpollist[-1]),', '.join(str(i) for i in MpProp[:-1]), 
            str(MpProp[-1])))
    exit()

# making the pot file
if args.oldpot: # NOT WORKING ANYMORE
    mypot="AU\n {0} {1} {2} 1 1\n".format(totatom, mulpollist[0], polarilist[0])
    k = 0
    for i in textlist:
        k += 1
        for j in i:
            spc=4-len(str(k))
            mypot += spc*" " + str(k) + 3*" " + j+"\n"
else:
    mypot = "! Potential made by MpProp2pot.py\n\
! from {0} MpProp files.\n".format(len(MpProp))
    coor = ""
    mult = ["","",""]
    pol  = ""
    atom, oldatom = 0, 0
    polsites = 0
    for i in textlist:
        for j in range(len(i[0])):
            # coordinates
            coor +=i[0][j] + i[1][j] + "\n"
        for j in range(len(i[2])):
            atom = oldatom
            for k in i[2][j]:
                atom += 1
                mult[j] += str(atom) + k + "\n"
        oldatom = atom
        for j in range(len(i[3])):
            # polarizabilites
            polsites += 1
            pol += str(polsites) + i[3][j] + "\n"
    mypot += "@COORDINATES\n{0}\nAA\n".format(totatom) + coor
    mypot += "@MULTIPOLES\n"
    for i in range(len(mult)):
        mypot += "ORDER {0}\n{1}\n".format(i, totatom) + mult[i]
    mypot += "@POLARIZABILITIES\nORDER 1 1\n{0}\n".format(totatom)+pol

    len_list = 3
    mypot += "EXCLISTS\n{0} {1}\n".format(totatom, len_list)
    atm1,atm2,atm3 = 1,2,3
    for i in range(totatom/len_list):
        mypot += "{0} {1} {2}\n{1} {0} {2}\n{2} {0} {1}\n".format(atm1,atm2,atm3)
        atm1 += 3
        atm2 += 3
        atm3 += 3
#    print mypot
    
outf=open(potfile, "w")
outf.write(mypot)
outf.close()
