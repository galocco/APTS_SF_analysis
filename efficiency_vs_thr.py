import ROOT
import matplotlib as mpl
import matplotlib.pyplot as plt

#dictionary with the conversion from 100e- to ADCu
hundredElectronToADCu = {
               "AF15_W13_1.2V":	109.2244092,
               "AF15_W22_1.2V":	108.5237472,
               "AF15B_W22_1.2V": 75.72872918,
               "AF15P_W22_1.2V": 76.58858776,
               "AF10P_W22_1.2V": 76.65509642,
               "AF20P_W22_1.2V": 76.42166474,
               "AF25P_W22_1.2V": 76.34448086,
               "AF15P_W22_0V":	43.9557306,
               "AF15P_W22_2.4V":	98.47832552,
               "AF15P_W22_3.6V":	110.8561877,
               "AF15P_W22_4.8V":	116.6778818
            }

#list of the analysis results path
file_path_list = ["/home/giacomo/APTS_SF_analysis/analyseDUT_347092422220828092436_2.root","/home/giacomo/APTS_SF_analysis/analyseDUT_000025.root"]
#list of the chips
chip_list = ["AF15P_W22_1.2V","AF25P_W22_1.2V"]
#list of the labels for the plot
label_list = ["15um (August)","25um (June)"]


fig, ax1 = plt.subplots(figsize=(11,5))
plt.subplots_adjust(left=0.07,right=0.75,top=0.95)

for file_path,label,chip in zip(file_path_list,label_list,chip_list):
   input_file = ROOT.TFile(file_path,"read")

   if label == "25um (June)":
      ntrackshist = input_file.Get("AnalysisEfficiency/APTS_4/eTotalEfficiency")
      cluster_ass= input_file.Get("AnalysisDUT/APTS_4/seedChargeAssociated")
   else:
      ntrackshist = input_file.Get("AnalysisEfficiency/APTS_3/eTotalEfficiency")
      cluster_ass= input_file.Get("AnalysisDUT/APTS_3/seedChargeAssociated")
   ntracks = ntrackshist.GetEfficiency(1)
   ntracks = int(cluster_ass.GetEntries()/ntracks)
   
   generated  = ROOT.TH1D("generated","",1,0,1)
   generated.SetBinContent(1, ntracks)
   generated.SetBinError(1, ROOT.TMath.Sqrt(ntracks))
   eff_list = []
   err_eff_up = []
   err_eff_low = []
   charge = []
   thr_list = [60,80,100,120,140,160,180,200,250,300,350]
   if label == "10um (August)":
      thr_list = [100,120,140,160,180,200,250,300,350]

   for thr in thr_list:
      thr_bin = cluster_ass.GetXaxis().FindBin(thr)
      nclusters = cluster_ass.Integral(thr_bin,cluster_ass.GetNbinsX())+cluster_ass.GetBinContent(cluster_ass.GetNbinsX()+1)
      passed  = ROOT.TH1D("passed",";;",1,0,1)
      passed.SetBinContent(1, nclusters)
      passed.SetBinError(1, ROOT.TMath.Sqrt(nclusters))
      eff = ROOT.TEfficiency(passed,generated)
      eff_list.append(eff.GetEfficiency(1))
      err_eff_up.append(eff.GetEfficiencyErrorUp(1))
      err_eff_low.append(eff.GetEfficiencyErrorLow(1))
      charge.append(100*thr/hundredElectronToADCu[chip])
      del passed
      del eff

   label = 'pixel pitch = '+label
   asymmetric_error = [err_eff_low, err_eff_up]
   ax1.errorbar(charge, eff_list, yerr=asymmetric_error, label=label, marker="s", linestyle='')

ax1.set_ylabel('Efficiency')
ax1.set_xlabel('Threshold (electrons)')
ax1.legend(loc='lower left')
ax1.grid()
ax1.set_ylim(0.69,1.01)

ax1.legend(loc='lower right',bbox_to_anchor =(1.32, -0.02),prop={"size":9})

x = 0.8
y = 0.95

ax1.text(
    x,y,
    '$\\bf{ITS3}$ beam test $\\it{preliminary}$',
    fontsize=12,
    ha='center', va='top',
    transform=ax1.transAxes
)

ax1.text(
    x,y-0.06,
    '@PS June 2022, 10 GeV/c protons\n@PS August 2022, 12 GeV/c protons',
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

fig.savefig('efficiencyVsThreshold.png', dpi=800)
plt.show()