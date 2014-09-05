#!/usr/bin/env python


#from pylab import matplotlib
import matplotlib.pyplot as plt
#from pylab import *
import argparse
import numpy as np
plt.rcParams.update({'font.size': 18})
from math import sqrt
try:
    from mpltools import style
    from mpltools import layout
except:
    pass

#rcParams.update({'figure.autolayout': True})

def get_time(input):
    tmp = ""
    hour, min, sec = 0.0, 0.0, 0.0
    for i in input:
        if i[0:6] =="minute":
            min = float(tmp)
        elif i[0:6] =="second":
            sec = float(tmp)
        elif i[0:4] == "hour":
            hour = float(tmp)
        tmp = i
    return hour*60.0 + min + sec/60.0

parser = argparse.ArgumentParser(
    formatter_class=argparse.RawTextHelpFormatter,
    description="\
Simple plot script.")

parser.add_argument("-i",dest="input",nargs='+',required=True, 
                    help="Input files")
parser.add_argument("-x",dest="x",
                    help="What to plot on the x-coordinate")
parser.add_argument("-y",dest="y",
                    help="What to plot on the y-coordinate")
parser.add_argument("-t","--title",dest="title",
                    help="Title")
parser.add_argument("-o",dest="output",
                    help="Output file (pdf)")
parser.add_argument("--loc",dest="loc",default="best",
                    help="Location of legends")
parser.add_argument("-s","--subplot",default=False, action='store_true',dest="subplot",
                    help="Make subplots")
parser.add_argument("--xlim",dest="xlim",nargs=2, type=float,
                    help="Range on the x-axis")
parser.add_argument("--ylim",dest="ylim",nargs=2, type=float,
                    help="Range on the y-axis")
parser.add_argument("--lw",dest="lw", type=float, default=2.0,
                    help="Linewidth")
parser.add_argument("--bw",default=False, action='store_true',dest="bw",
                    help="Make black and white figure")
parser.add_argument("--noleg",default=False, action='store_true',dest="noleg",
                    help="No legend")
parser.add_argument("--stderror",default=False, action='store_true',dest="stderror",
                    help="Use standard error instead of standard deviation")

args = parser.parse_args()
x = args.x
y = args.y
inp = args.input
labloc = 1
xlim = args.xlim
ylim = args.ylim

if args.loc:
    labloc = args.loc

if args.bw:
    lcolor = ['k','0.75','0.5','k','0.75','0.5']
    lstyle = ['-','--','-','--','-','--','-','--','-','--','-','--']
    linestyle = ['k-','k.','k-.','k^','k.','k<']
else:
    linestyle = ['b-','g-','r-','y-','k-','b-','g-','r-','y-','k-']
    lcolor = ['#348ABD', '#7A68A6', '#A60628', '#467821', '#CF4457', '#188487', '#E24A33','burlywood']
    lstyle = ['-','-','-','-','-','-','-','-','-','-','-','-','-']

mark = ['o','^','<','v','>','o','^','<','v','>']

time_plot = False
allx=[]
ally=[]
for i in inp:
    file = open(i,"r")
    lines = file.readlines()
    file.close()
    for k in range(5):
        try:
            words = lines[k].split()
            first = words[0]
        except:
            first = ""
        if first =="x:" and not x:
            x=words[1]
            xlab = lines[k][3:].rstrip()
        elif first =="y:" and not y:
            y=words[1]
            ylab = lines[k][3:].rstrip()
    if x=="time" or y=="time":
        time_plot = True

    allx.append(x)
    ally.append(y)

for i in ally:
    if i != ally[0]:
        quit("Not the same y-coordinates: "+ally[0]+" and "+i)
for i in allx:
    if i != allx[0]:
        quit("Not the same x-coordinates: "+allx[0]+" and "+i)

if x=="exc":
    xlab = 'Excitation energy (eV)'
elif x=="tpa":
    xlab = 'Two-photon absorption cross section (GM)'
elif x=="rad":
    xlab = 'Polarization threshold ($\AA$)'
elif x=="rad2":
    xlab = 'Threshold ($\AA$)'
elif x=="sites":
    xlab = 'Number of atoms within threshold'
elif x=="time":
    xlab = 'Wall time (min)'
elif x and not xlab:
    xlab = x
#    quit("no good x-values specified: "+x)

if y=="exc":
    ylab = 'Excitation energy (eV)'
elif y=="tpa":
    ylab = 'Two-photon absorption cross section (GM)'
elif y=="rad":
    ylab = 'Cut threshold (AA)'
elif y=="sites":
    ylab = 'Number of atoms within threshold'
elif y=="time":
    ylab = 'Wall time (min)'
elif y and not ylab:
    ylab = y
#    quit("no good y-values specified: "+y)

if args.subplot:
    pagesize = 4*len(inp)
    plt.rcParams['figure.figsize'] = 6, pagesize
    numplot = 0
    totplot = len(inp)
    f, subplt = plt.subplots(totplot, 1 , sharex=True)#, subplot_kw=dict(aspect=1))
num = 0
title = False
for i in inp:
    md = False
    lab = False
    scatter = False
    def_color = False
    if not args.ylim:
        ylim = False
    if not args.xlim:
        xlim = False
    xaxes = []
    yaxes = []
    file = open(i,"r")
    lines = file.readlines()
    file.close()
    for k in range(10):
        try:
            words = lines[k].split()
            first = words[0]
        except:
            first = ""
        if first == "label:":
            lab = lines[k][7:-1]
        if first == "title:":
            title = lines[k][7:-1]
        elif first == "loc:" and not args.loc:
            labloc = int(words[1])
        elif first == "type:" and words[1] == "md":
            md = True
        elif first == "type:" and words[1] == "scatter":
            scatter = True
        elif first == "xlim:":
            xlim = [float(words[1]),float(words[2])]
        elif first == "ylim:":
            ylim = [float(words[1]),float(words[2])]
        elif first == "color:":
            def_color = words[1]
    if md:
        stdev = []

# Read data
    for j in lines:
        try:
            xaxes.append(float(j.split()[0]))
            if time_plot:
                yaxes.append(get_time(j.split()[1:]))
            else:
                yaxes.append(float(j.split()[1]))
            if md:
                if args.stderror:
                    stdev.append(float(j.split()[2])/sqrt(50))
                else:
                    stdev.append(float(j.split()[2]))
        except:
            continue
    # color on graph:
    if not def_color:
        if args.subplot:
            def_color = lcolor[0]
        else:
            def_color = lcolor[num]
# label
    if not lab:
        lab = i[7:].split(".")[0].split("_")[0]

    # make subplots
    ax = plt.subplot(111)    
    if args.subplot:
        ax = subplt[numplot]
        ax.grid(True)
        if numplot == int(totplot/2):
            ax.set_ylabel(ylab)
        if numplot == totplot-1:
            ax.set_xlabel(xlab)
        if md:
            ax.errorbar(xaxes,yaxes,yerr=stdev,color=def_color,ls=lstyle[0],label=lab, lw=args.lw, marker='o', elinewidth=args.lw, capsize=2.5*args.lw, markeredgewidth=args.lw)
        else:
            ax.plot(xaxes,yaxes,marker="o",lw=args.lw,label=lab,color=def_color,ls=lstyle[0], markeredgewidth=args.lw)
            # ax.legend(loc=labloc,markerscale=0.1).get_frame().set_alpha(0)
        if ylim:
            ymin = ylim[0]
            ymax = ylim[1]
        else:
            ydiff = (max(yaxes)-min(yaxes))*0.05
            ymax = max([max(yaxes),round(max(yaxes),2)]) + ydiff
            ymin = min([min(yaxes),round(min(yaxes),2)]) - ydiff
            if md:
                ymax += stdev[yaxes.index(max(yaxes))]
                ymin -= stdev[yaxes.index(min(yaxes))]

            ax.yaxis.set_ticks(np.arange(round(min(yaxes),2), round(max(yaxes),2), 0.02))
        ax.set_ylim([ymin,ymax])
        ax.annotate(lab, xy=(0.24, 0.8), xycoords='axes fraction', fontsize=20)
        numplot += 1
    elif md:
        plt.errorbar(xaxes,yaxes,yerr=stdev,color=def_color,ls=lstyle[num],label=lab, lw=args.lw, marker=mark[num], elinewidth=args.lw, capsize=2.5*args.lw, markeredgewidth=args.lw)
    elif scatter:
        plt.scatter(xaxes,yaxes,label=lab,color=def_color, lw=args.lw, marker=mark[num])
    else:
        plt.plot(xaxes,yaxes,marker=mark[num],color=def_color,ls=lstyle[num],lw=args.lw,label=lab, markeredgewidth=args.lw)
    num += 1
    if xlim:
        plt.xlim(xlim)

# What is this?
plt.subplots_adjust(left=0.15)

if not args.subplot and y=="exc" and ylim:
    plt.yticks(np.arange(0, 10, 0.02))

if not args.subplot:
    plt.xlabel(xlab)
    plt.ylabel(ylab)
    if args.ylim:
        plt.ylim(args.ylim)
    if args.xlim:
        plt.xlim(args.xlim)
#xlabel(xlab,fontsize=20)
#ylabel(ylab,fontsize=20)

if args.output:
    figname = args.output
else:
    figname = "tmp.pdf"

if figname[-4:] != ".pdf":
    figname += ".pdf"
elif  figname[-4:] == ".png":
    figname = figname[-4:]+".pdf"

if args.subplot:
    f.subplots_adjust(hspace=0)
else:
    box = ax.get_position()
    if labloc == "outside":
        ax.set_position([box.x0*1.2, box.y0, box.width, box.height*0.80])
        if len(args.input) < 5:
            ncol = 2
        else:
            ncol = 3
        plt.legend(loc='upper center', bbox_to_anchor=(0.5, 1.35),
                   ncol=ncol,fancybox=True, shadow=True)
    else:
        ax.set_position([box.x0*1.2, box.y0, box.width, box.height])
        if not args.noleg:
            plt.legend(loc=labloc, fancybox=True, shadow=True)
    plt.grid(True)

    if args.title:
        ax.set_title(args.title)
    elif title:
        ax.set_title(title)

print "making "+figname
plt.savefig(figname,format='pdf')
