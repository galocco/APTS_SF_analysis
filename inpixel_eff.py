#!/usr/bin/env python3

import numpy as np
from matplotlib import pyplot as plt
from matplotlib import patches as pat
from plotting_utils import plot_parameters, add_beam_info
import os
import ROOT
from utils import utils
import re
script_dir=os.path.dirname(os.path.realpath(__file__))
import math
chip = "AF15P_W22_1.2V"
apts = "3"

file_path = "data/analysis_run413221453_221013042711_thr120.root"
pitch = 15


chip = "AF10P_W22_1.2V"
apts = "3"
label = "AF15P_W22B2"

file_path = "/home/giacomo/its-corryvreckan-tools/output/SPSOctober22/B1/AF10P_W22B28/analysis_415000658221014000702_DUT_thr160.root"
pitch = 10
size_in_bin = 15
label = "AF10P_W22B28"
#chip = "AF25P_W22_1.2V"
if chip == "AF25P_W22_1.2V":
    apts = "4"
    label = "AF25P_W22B7"
    pitch = 25
    file_path = "/home/giacomo/its-corryvreckan-tools/output/SPSOctober22/B1/AF25P_W22B7/analysis_416153058221015153104_DUT_thr160.root"
data = ROOT.TFile(file_path,"read")
thr = int(re.findall(r'\d+', file_path)[-1])*100/utils.hundredElectronToADCu[chip] 
efficiency = data.Get("AnalysisEfficiency/APTS_"+apts+"/pixelEfficiencyMap_trackPos")
#efficiency = data.Get("AnalysisEfficiency/APTS_3/pixelEfficiencyMap_trackPos")

cv = ROOT.TCanvas("cv","cv")
passed = efficiency.GetPassedHistogram()
total = efficiency.GetTotalHistogram()
passed.Draw("colz")



def integrate(hist):
    for i in range(1,int(size_in_bin/2)+1 ):
        #cross
        tot = hist.GetBinContent(int(size_in_bin/2)+1 +i,int(size_in_bin/2)+1 )
        tot += hist.GetBinContent(int(size_in_bin/2)+1 -i,int(size_in_bin/2)+1 )
        tot += hist.GetBinContent(int(size_in_bin/2)+1 ,int(size_in_bin/2)+1 +i)
        tot += hist.GetBinContent(int(size_in_bin/2)+1 ,int(size_in_bin/2)+1 -i)

        hist.SetBinContent(int(size_in_bin/2)+1 ,int(size_in_bin/2)+1 +i,int(tot))
        #hist.SetBinError(int(size_in_bin/2)+1 ,int(size_in_bin/2)+1 +i,math.sqrt(int(tot)))
        hist.SetBinContent(int(size_in_bin/2)+1 ,int(size_in_bin/2)+1 -i,int(tot))
        #hist.SetBinError(int(size_in_bin/2)+1 ,int(size_in_bin/2)+1 -i,math.sqrt(int(tot)))
        hist.SetBinContent(int(size_in_bin/2)+1 -i,int(size_in_bin/2)+1 ,int(tot))
        #hist.SetBinError(int(size_in_bin/2)+1 -i,int(size_in_bin/2)+1 ,math.sqrt(int(tot)))
        hist.SetBinContent(int(size_in_bin/2)+1 +i,int(size_in_bin/2)+1 ,int(tot))
        #hist.SetBinError(int(size_in_bin/2)+1 +i,int(size_in_bin/2)+1 ,math.sqrt(int(tot)))
        
    for i in range(1,int(size_in_bin/2)+1 ):
        #diagonale
        tot = hist.GetBinContent(int(size_in_bin/2)+1 +i,int(size_in_bin/2)+1 +1)
        tot += hist.GetBinContent(int(size_in_bin/2)+1 -i,int(size_in_bin/2)+1 -1)
        tot += hist.GetBinContent(int(size_in_bin/2)+1 -i,int(size_in_bin/2)+1 +i)
        tot += hist.GetBinContent(int(size_in_bin/2)+1 +i,int(size_in_bin/2)+1 -i)
        hist.SetBinContent(int(size_in_bin/2)+1 +i,int(size_in_bin/2)+1 +i,int(tot))
        #hist.SetBinError(int(size_in_bin/2)+1 +i,int(size_in_bin/2)+1 +i,math.sqrt(int(tot)))
        hist.SetBinContent(int(size_in_bin/2)+1 -i,int(size_in_bin/2)+1 -i,int(tot))
        #hist.SetBinError(int(size_in_bin/2)+1 -i,int(size_in_bin/2)+1 -i,math.sqrt(int(tot)))


    for i in range(1,int(size_in_bin/2)):
        ####spigolo
        tot = hist.GetBinContent(int(size_in_bin/2)+1 +i,size_in_bin)
        tot += hist.GetBinContent(int(size_in_bin/2)+1 -i,size_in_bin)
        tot += hist.GetBinContent(int(size_in_bin/2)+1 +i,1)
        tot += hist.GetBinContent(int(size_in_bin/2)+1 -i,1)
        #alto destra
        hist.SetBinContent(int(size_in_bin/2)+1 +i,size_in_bin,int(tot))
        #hist.SetBinError(int(size_in_bin/2)+1 +i,size_in_bin,math.sqrt(int(tot)))
        #alto sinistra
        hist.SetBinContent(int(size_in_bin/2)+1 -i,size_in_bin,int(tot))
        #hist.SetBinError(int(size_in_bin/2)+1 -i,size_in_bin,math.sqrt(int(tot)))
        #basso destra
        hist.SetBinContent(int(size_in_bin/2)+1 +i,1,int(tot))
        #hist.SetBinError(int(size_in_bin/2)+1 +i,1,math.sqrt(int(tot)))
        #basso sinistra
        hist.SetBinContent(int(size_in_bin/2)+1 -i,1,int(tot))
        #hist.SetBinError(int(size_in_bin/2)+1 -i,1,math.sqrt(int(tot)))
        hist.SetBinContent(size_in_bin,int(size_in_bin/2)+1 +i,int(tot))
        #hist.SetBinError(size_in_bin,int(size_in_bin/2)+1 +i,math.sqrt(int(tot)))
        hist.SetBinContent(size_in_bin,int(size_in_bin/2)+1 -i,int(tot))
        #hist.SetBinError(size_in_bin,int(size_in_bin/2)+1 -1,math.sqrt(int(tot)))
        hist.SetBinContent(1,int(size_in_bin/2)+1 +i,int(tot))
        #hist.SetBinError(1,int(size_in_bin/2)+1 +i,math.sqrt(int(tot)))
        hist.SetBinContent(1,int(size_in_bin/2)+1 -i,int(tot))
        #hist.SetBinError(1,int(size_in_bin/2)+1 -i,math.sqrt(int(tot)))

    return hist
passed = integrate(passed)
total = integrate(total)
efficiency_merged = ROOT.TEfficiency(passed,total)
print(total.GetName())
print(passed.GetName())
cv.SaveAs("passed.png")
total.Draw("colz")
cv.SaveAs("total.png")
#eff measurement
eff_merged = []
errup_merged = []
errlow_merged = []
counter = 0
efficiency = data.Get("AnalysisEfficiency/APTS_"+apts+"/pixelEfficiencyMap_trackPos")

for j in range(0,size_in_bin):
    for i in range(0,size_in_bin):
        counter +=1
        eff_merged.append(100*efficiency_merged.GetEfficiency(i+(size_in_bin+2)*j+size_in_bin+3))
        errup_merged.append(100*efficiency_merged.GetEfficiencyErrorUp(i+(size_in_bin+2)*j+size_in_bin+3))
        errlow_merged.append(100*efficiency_merged.GetEfficiencyErrorLow(i+(size_in_bin+2)*j+size_in_bin+3))
        
eff_merged = np.array(eff_merged).reshape(size_in_bin,size_in_bin)
errup_merged = np.array(errup_merged).reshape(size_in_bin,size_in_bin)
errlow_merged = np.array(errlow_merged).reshape(size_in_bin,size_in_bin)

##plot
eff = []
errup = []
errlow = []

counter = 0
for j in range(0,size_in_bin):
    for i in range(0,size_in_bin):
        eff.append(100*efficiency.GetEfficiency(i+(size_in_bin+2)*j+size_in_bin+3))
        errup.append(100*efficiency.GetEfficiencyErrorUp(i+(size_in_bin+2)*j+size_in_bin+3))
        errlow.append(100*efficiency.GetEfficiencyErrorLow(i+(size_in_bin+2)*j+size_in_bin+3))
        
min_eff = 90 #min(eff)
print(min_eff)
eff = np.array(eff).reshape(size_in_bin,size_in_bin)
errup = np.array(errup).reshape(size_in_bin,size_in_bin)
errlow = np.array(errlow).reshape(size_in_bin,size_in_bin)

tot_eff = data.Get("AnalysisEfficiency/APTS_"+apts+"/eTotalEfficiency").GetEfficiency(1)*100
c = ['tab:red','tab:blue','tab:green']

d = size_in_bin/2.
na = int(size_in_bin/2)

d_p = pitch/2.
na_p = int(pitch/2.)

fig,ax=plt.subplots(1,2,figsize=(10.5,4))
plt.subplots_adjust(wspace=0.5,top=0.98,left=0.1,right=0.84,bottom=0.03)
plt.sca(ax[0])
im = plt.imshow(eff,extent=[-pitch/2.,pitch/2.,-pitch/2.,pitch/2.],vmin=min_eff,vmax=100,origin='lower',cmap='inferno')
cb = plt.colorbar(im,pad=0.015,fraction=0.0474)
for i in range(na_p):
    plt.arrow(0,i*d_p/na_p,0,d_p/na_p,head_width=0.3, head_length=0.3,color=c[0],length_includes_head=True,zorder=100,clip_on=False)
    plt.arrow(i*d_p/na_p,d_p,d_p/na_p,0,head_width=0.3, head_length=0.3,color=c[1],length_includes_head=True,zorder=100,clip_on=False)
    plt.arrow(d_p-i*d_p/na_p, d_p-i*d_p/na_p, -d_p/na_p, -d_p/na_p,head_width=0.3, head_length=0.3,color=c[2],length_includes_head=True,zorder=100,clip_on=False)
plt.plot([0],[0],marker='.',color=c[0],zorder=99,clip_on=False)
plt.plot([0],[d_p],marker='.',color=c[1],zorder=99,clip_on=False)
plt.plot([d_p],[d_p],marker='.',color=c[2],zorder=99,clip_on=False)
ax[0].add_patch(pat.Circle((-4.5,4.5),2.11,color='white',alpha=0.33))
plt.annotate('Tracking\nresolution\n$\sigma=2.11$ µm', (-4.5,4.5), color='white', horizontalalignment='center', verticalalignment='center')
plt.annotate('A', (0,0), color=c[0], fontweight="bold", xytext=(0,-4), textcoords='offset points', horizontalalignment='center', verticalalignment='top')
plt.annotate('B', (0,d_p), color=c[1], fontweight="bold", xytext=(0,2), textcoords='offset points', horizontalalignment='center',  verticalalignment='bottom')
plt.annotate('C', (d_p,d_p), color=c[2], fontweight="bold", xytext=(0,2), textcoords='offset points', horizontalalignment='center', verticalalignment='bottom')
cb.set_label("Detection efficiency (%)")
plt.xticks([-pitch/2,-pitch/3,-pitch/6,0,pitch/6,pitch/3,pitch/2])
plt.yticks([-pitch/2,-pitch/3,-pitch/6,0,pitch/6,pitch/3,pitch/2])
plt.xlabel("In-pixel track intercept x (µm)")
plt.ylabel("In-pixel track intercept y (µm)")
plt.xlim(-pitch/2,pitch/2)
plt.ylim(-pitch/2,pitch/2)

n = 10000

def matrix_to_path(mat):
    return np.array([
        [mat[int(size_in_bin/2.)][int(size_in_bin/2.)+int(round(dx))] for dx in np.linspace(0,d,n,endpoint=False)],
        [mat[int(size_in_bin/2.)+int(round(dx))][-1] for dx in np.linspace(0,d,n,endpoint=False)],
        [mat[int(size_in_bin/2.)+int(round(dx))][int(size_in_bin/2.)+int(round(dx))] for dx in np.linspace(0,d,n,endpoint=False)[::-1]],
    ])

y     = matrix_to_path(eff_merged)
yelow = matrix_to_path(errlow_merged)
yeup  = matrix_to_path(errup_merged)
d = d*pitch/size_in_bin
x = np.array([
    np.linspace(0,d,n,endpoint=False),
    np.linspace(d,2*d,n,endpoint=False),
    np.linspace(2*d,2*d+d*np.sqrt(2),n,endpoint=False)
])

plt.sca(ax[1])
for i in range(3):
    # plt.errorbar(x[i],y[i],yerr=(yelow[i],yeup[i]),color=c[i],\
    #     errorevery=[int(n/d),(0,int(n/d)),(int(n/d/2),int(n/d))][i],\
    #     capsize=1.5
    # )
    plt.fill([*x[i],*x[i][::-1]],[*(yeup[i]+y[i]),*(-yelow[i]+y[i])[::-1]],c=c[i],alpha=.3)
    plt.plot(x[i],y[i],color=c[i])
    # plt.plot([x[i][int(n/d*4+(0 if i!=2 else n/d/2))]],[y[i][int(n/d*4+(0 if i!=2 else n/d/2))]],'>',c=c[i])
plt.xlim(x[0][0]-0.1,x[-1][-1])
plt.xticks([0,pitch/2,pitch,pitch*3/2])
plt.ylim(min_eff,100)
plt.grid(axis='both')
plt.xlabel("Distance along the path (µm)")
plt.ylabel("Detection efficiency (%)")
secax = ax[1].secondary_xaxis('top')
secax.set_xticks([x[0][0],x[1][0],x[2][0],x[2][-1]])
for i,t in enumerate(secax.set_xticklabels(['A','B','C','A'])):
    t.set_color(c[i%3])
plt.axhline(tot_eff,linestyle='dotted',color='grey')
plt.text(14.5,tot_eff,f"Total efficiency",ha='center', va='bottom',color='grey')
# plt.text(x[2][-1]*0.99,tot_eff,f"Total efficiency = {round(tot_eff,1)}%",ha='right', va='bottom',color='grey')

ax[1].add_patch(pat.Rectangle((0.5,75.5),11,3,facecolor="white",edgecolor="grey",linewidth=0.5,zorder=9))
ax[1].add_patch(pat.Rectangle((1,76),1,2,color=c[0],alpha=0.3,zorder=9))
ax[1].add_patch(pat.Rectangle((2,76),1,2,color=c[1],alpha=0.3,zorder=9))
ax[1].add_patch(pat.Rectangle((3,76),1,2,color=c[2],alpha=0.3,zorder=9))
plt.annotate(xy=(4.5,77), text="Stat. error", verticalalignment="center",zorder=9)

# plt.axvline(x[1][0],color=c[1],linestyle='--',linewidth=0.5)
# plt.axvline(x[2][0],color=c[2],linestyle='--',linewidth=0.5)


asp = np.diff(ax[1].get_xlim())[0] / np.diff(ax[1].get_ylim())[0]
ax[1].set_aspect(asp*0.95)
# plt.tight_layout()

CHIP_SETTINGS = '\n'.join([
    '$\\bf{%s}$' % label,
    #'type: %s'%'modified with gap',
    'split:  %s' % '4',
    #'$V_{sub}=V_{pwell}$ = -1.2 V',
    '$I_{reset}=%s\,\\mathrm{pA}$' % 100,
    '$I_{biasn}=%s\,\\mathrm{\mu A}$' % 5,
    '$I_{biasp}=%s\,\\mathrm{\mu A}$' % 0.5,
    '$I_{bias4}=%s\,\\mathrm{\mu A}$' % 150,
    '$I_{bias3}=%s\,\\mathrm{\mu A}$' % 200,
    '$V_{reset}=%s\,\\mathrm{mV}$' % 500,
    'thr = %s$e^{-}$' % int(thr) 
])

add_beam_info(ax[0],y=0.14)

ax[1].text(1.1, 1.0,
                   CHIP_SETTINGS,
                   fontsize=9,
                   ha='left', va='top',
                   transform=ax[1].transAxes
                   )

plt.savefig("ALICE-ITS3_"+chip+"_inpix_eff_"+str(int(thr))+"e.pdf")
plt.savefig("ALICE-ITS3_"+chip+"_inpix_eff_"+str(int(thr))+"e.png")
plt.show()

