import ROOT
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-a', '--adc', help='Plot in ADCu', action='store_true')
args = parser.parse_args()

ADCu = args.adc

hundredElectronToADCu = {
              "AF15_W13_1.2V":   113.5602885,
               "AF15_W22_1.2V":  112.6764784,
               "AF15B_W22_1.2V": 79.90360556,
               "AF15P_W22_1.2V": 79.82152217,
               "AF10P_W22_1.2V": 80.31095738,
               "AF20P_W22_1.2V": 80.09704306,
               "AF25P_W22_1.2V": 79.86636469,
               "AF15P_W22_0V":   44.7844201,
               "AF15P_W22_2.4V": 103.97717,
               "AF15P_W22_3.6V": 116.4895804,
               "AF15P_W22_4.8V": 122.3611669,
               "AF15P_W22B8":    79.48599865,
               "AF15P_W22B11":   80.27620951,
               "AF15P_W22B15":   85.8128149
            }
            

#list of the analysis results path
file_path_list = [
                  "SPSRes/alignment_416153058221015153104_DUT_cut60_3.root",
                  "SPSRes/alignment_422131231221018134906_DUT_cut60_3.root",
                  "SPSRes/alignment_000801_DUT_cut60_3.root"
         ]

list_of_files = [
                  "SPSRes/alignment_416153058221015153104_DUT_FHR.root",
                  "SPSRes/alignment_422131231221018134906_DUT_FHR.root",
                  "SPSRes/alignment_000801_DUT_FHR.root"
         ]
#list of the chips
#list of the chips
chip_list = ["AF15P_W22_0V","AF15P_W22_1.2V","AF15P_W22_1.2V"]
#list of the labels for the plot
label_list = ["25P","10B","15P"]

color_list = ['b', 'black', 'r', 'g', 'orange']

n_pixels = 16

fig, ax1 = plt.subplots(figsize=(11,5))
plt.subplots_adjust(left=0.07,right=0.75,top=0.95)

ax2 = ax1.twinx()

ax1.errorbar([],[],([],[]),label="Efficiency",marker='s',elinewidth=1.3,capsize=1.5,color='dimgrey')
ax1.errorbar([],[],([],[]),label="Fake Hit Rate",marker='s',markerfacecolor='none',linestyle='dashed',elinewidth=1.3,capsize=1.5,color='dimgrey')

list_of_thr = [60,80,100,120,150,170,200,225,250,300]


for file_path,label,chip,color in zip(file_path_list,label_list,chip_list,color_list):
   input_file = ROOT.TFile(file_path,"read")

   if label == "25um (June)":
      ntrackshist = input_file.Get("AnalysisEfficiency/APTS_4/eTotalEfficiency")
      cluster_ass= input_file.Get("AnalysisDUT/APTS_4/seedChargeAssociated")
   else:
      ntrackshist = input_file.Get("AnalysisEfficiency/APTS_3/eTotalEfficiency")
      cluster_ass= input_file.Get("AnalysisDUT/APTS_3/seedChargeAssociated")
   cluster_ass.SetName(chip)
   ntracks = ntrackshist.GetEfficiency(1)
   ntracks = round(cluster_ass.GetEntries()/ntracks)

   generated  = ROOT.TH1D("generated","",1,0,1)
   generated.SetBinContent(1, ntracks)
   generated.SetBinError(1, ROOT.TMath.Sqrt(ntracks))
   eff_list = []
   err_eff_up = []
   err_eff_low = []
   charge = []

   for thr in list_of_thr:
      thr_bin = cluster_ass.GetXaxis().FindBin(thr)
      nclusters = cluster_ass.Integral(thr_bin,cluster_ass.GetNbinsX())+cluster_ass.GetBinContent(cluster_ass.GetNbinsX()+1)
      passed  = ROOT.TH1D("passed",";;",1,0,1)
      passed.SetBinContent(1, nclusters)
      passed.SetBinError(1, ROOT.TMath.Sqrt(nclusters))
      eff = ROOT.TEfficiency(passed,generated)
      eff_list.append(100*eff.GetEfficiency(1))
      err_eff_up.append(100*eff.GetEfficiencyErrorUp(1))
      err_eff_low.append(100*eff.GetEfficiencyErrorLow(1))
      if ADCu:
        charge.append(100*thr/hundredElectronToADCu[chip])
      else:
        charge.append(thr)
      del passed
      del eff

   asymmetric_error = [err_eff_low, err_eff_up]
   ax1.errorbar(charge, eff_list, yerr=asymmetric_error, label=label, marker="s", linestyle='-',color=color)

for file,label,color,chip in zip(list_of_files, label_list, color_list,chip_list):

    tfile = ROOT.TFile(file,"read")

    if label == "25um (June)":
        hist = tfile.Get("EventLoaderEUDAQ2/APTS_4/hPixelRawValues")#To be changed for June data
    else:
        hist = tfile.Get("EventLoaderEUDAQ2/APTS_3/hPixelRawValues")#To be changed for June data

    charge =  []
    fake_hit_rate_list = []
    n_events = (hist.GetEntries()-hist.GetBinContent(0))/n_pixels

    for thr in list_of_thr:
        bin_min = hist.GetXaxis().FindBin(thr)
        clusters = hist.Integral(bin_min, hist.GetNbinsX()+1)
        fake_hit_rate_list.append(clusters/n_pixels/n_events)
        if ADCu:
            charge.append(100*thr/hundredElectronToADCu[chip])
        else:
            charge.append(thr)
    ax2.errorbar(charge, fake_hit_rate_list, label=label, marker="s", linestyle='dashed',markerfacecolor='none',color=color)


ax2.set_ylabel("P(pixel above Threshold)")
#ax2.set_yscale('log')

ax1.set_ylabel('Efficiency (%)')
if ADCu:
    ax1.set_xlabel('Threshold (ADCu)')
else:
    ax1.set_xlabel('Threshold (electrons)')
ax1.grid(axis='both')
ax1.set_ylim(69,101)
ax2.set_ylim(0,1)
ax2.minorticks_off()
ax1.axhline(99,linestyle='dashed',color='grey')
ax1.text(ax1.get_xlim()[0]-0.014*(ax1.get_xlim()[1]-ax1.get_xlim()[0]),99,"99",fontsize=7,ha='right', va='center')
h1, l1 = ax1.get_legend_handles_labels()
ax1.legend(h1[:1]+h1[1:],l1[:1]+l1[1:],loc='lower center',bbox_to_anchor=(1.22, -0.01),prop={"size":9})

x = 0.75
y = 0.9

ax1.text(
    x,y,
    '$\\bf{ALICE\ ITS3}$ beam test WORK IN PROGRESS',
    fontsize=12,
    ha='center', va='top',
    transform=ax1.transAxes
)

ax1.text(
    x,y-0.06,
    '@SPS October 2022, 120 GeV/c protons and pions',
    fontsize=9,
    ha='center', va='top',
    transform=ax1.transAxes
)

ax1.text(1.1,1.0,
    '\n'.join([
        '$\\bf{%s}$'%'APTS\ SF',
        'type: %s'%'modified with gap',
        'split:  %s'%'4',
        '$V_{sub}=V_{pwell}$ = -1.2 V',
        '$I_{reset}=%s\,\\mathrm{pA}$' %100,
        '$I_{biasn}=%s\,\\mathrm{\mu A}$' %5,
        '$I_{biasp}=%s\,\\mathrm{\mu A}$' %0.5,
        '$I_{bias4}=%s\,\\mathrm{\mu A}$' %150,
        '$I_{bias3}=%s\,\\mathrm{\mu A}$' %200,
        '$V_{reset}=%s\,\\mathrm{mV}$' %500
    ]),
    fontsize=9,
    ha='left', va='top',
    transform=ax1.transAxes
    )

if ADCu:
    fig.savefig('eff_fhr_VsThresholdInADCu.png', dpi=600)
else:
    fig.savefig('eff_fhr_VsThreshold.png', dpi=600)
#plt.show()