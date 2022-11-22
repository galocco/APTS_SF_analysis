import ROOT
import matplotlib as mpl
import matplotlib.pyplot as plt
import math
suffix = 'type_scs_rms'
#from ROOT import TCanvas
#dictionary with the conversion from 100e- to ADCu
hundredElectronToADCu = {
                "AF15_W13_1.2V": 113.5602885,
                "AF15_W22_1.2V": 112.6764784,
                "AF15B_W22_1.2V": 79.90360556,
                "AF15P_W22_1.2V": 79.82152217,
                "AF10P_W22_1.2V": 80.31095738,
                "AF20P_W22_1.2V": 80.09704306,
                "AF25P_W22_1.2V": 79.86636469,
                "AF15P_W22_0V": 44.7844201,
                "AF15P_W22_2.4V": 103.97717,
                "AF15P_W22_3.6V": 116.4895804,
                "AF15P_W22_4.8V": 122.3611669,
                "AF15P_W22B8":       79.48599865,
                "AF15P_W22B11":      80.27620951,
                "AF15P_W22B15":      85.8128149
            }

#tracking resolution from telescope-optimizer
tracking_resolution = 2.4
#list of the chips
chip_list = ["AF15P_W22_1.2V","AF15B_W22_1.2V","AF15_W13_1.2V","AF15_W22_1.2V"]
#chip_list = ["AF15P_W22_1.2V","AF15P_W22_1.2V","AF10P_W22_1.2V","AF10P_W22_1.2V"]
#chip_list = ["AF15P_W22_1.2V","AF15_W22_1.2V"]
#list of the labels for the plot
#label_list = ["Irradiated 10^15"]
#label_list = ["15P baseline = average frames [0,95]","15P baseline = frame 98","10P baseline = average frames [0,95]","10P baseline = frame 98"]
label_list = ["AF15P_W22","AF15B_W22","AF15_W13","AF15_W22"]
#label_list = ["AF15P","AF15"]

color_list = ['black','blue','red','green','orange']
#
#415000658221014000702
file_path_list_list = [
   [
      "SPSRes/analysis_413221453221013042711_DUT_thr80.root",
      "SPSRes/analysis_413221453221013042711_DUT_thr100.root",
      "SPSRes/analysis_413221453221013042711_DUT_thr120.root",
      "SPSRes/analysis_413221453221013042711_DUT_thr140.root",
      "SPSRes/analysis_413221453221013042711_DUT_thr160.root",
      "SPSRes/analysis_413221453221013042711_DUT_thr200.root",
      "SPSRes/analysis_413221453221013042711_DUT_thr250.root",
      "SPSRes/analysis_413221453221013042711_DUT_thr300.root"
   ],
   [
      "SPSRes/analysis_417165943221016165948_DUT_thr80.root",
      "SPSRes/analysis_417165943221016165948_DUT_thr100.root",
      "SPSRes/analysis_417165943221016165948_DUT_thr120.root",
      "SPSRes/analysis_417165943221016165948_DUT_thr140.root",
      "SPSRes/analysis_417165943221016165948_DUT_thr160.root",
      "SPSRes/analysis_417165943221016165948_DUT_thr200.root",
      "SPSRes/analysis_417165943221016165948_DUT_thr250.root",
      "SPSRes/analysis_417165943221016165948_DUT_thr300.root"
   ],
   [
      "SPSRes/analysis_422104101221018104107_DUT_thr80.root",
      "SPSRes/analysis_422104101221018104107_DUT_thr100.root",
      "SPSRes/analysis_422104101221018104107_DUT_thr120.root",
      "SPSRes/analysis_422104101221018104107_DUT_thr140.root",
      "SPSRes/analysis_422104101221018104107_DUT_thr160.root",
      "SPSRes/analysis_422104101221018104107_DUT_thr200.root",
      "SPSRes/analysis_422104101221018104107_DUT_thr250.root",
      "SPSRes/analysis_422104101221018104107_DUT_thr300.root"
   ],
   [
      "SPSRes/analysis_421225802221017225807_DUT_thr80.root",
      "SPSRes/analysis_421225802221017225807_DUT_thr100.root",
      "SPSRes/analysis_421225802221017225807_DUT_thr120.root",
      "SPSRes/analysis_421225802221017225807_DUT_thr140.root",
      "SPSRes/analysis_421225802221017225807_DUT_thr160.root",
      "SPSRes/analysis_421225802221017225807_DUT_thr200.root",
      "SPSRes/analysis_421225802221017225807_DUT_thr250.root",
      "SPSRes/analysis_421225802221017225807_DUT_thr300.root"
   ]
   
]

#415000658221014000702

binary_resolution_list = [15./math.sqrt(12),15./math.sqrt(12),15./math.sqrt(12),15./math.sqrt(12),10./math.sqrt(12)]
#binary_resolution = 15./math.sqrt(12)
thr_list = [
   80,
   100,
   120,
   140,
   160,
   200,
   250,
   300
]


hist = []
fig, ax1 = plt.subplots(figsize=(11,5))
plt.subplots_adjust(left=0.07,right=0.75,top=0.95)

ax2 = ax1.twinx()

ax1.errorbar([],[],([],[]),label="x-position resolution ",marker='s',elinewidth=1.3,capsize=1.5,color='dimgrey')
ax1.errorbar([],[],([],[]),label="y-position resolution",marker='s',markerfacecolor='none',linestyle='dashed',elinewidth=1.3,capsize=1.5,color='dimgrey')
ax1.errorbar([],[],([],[]),label="cluster size",marker='o',markerfacecolor='none',linestyle='dashed',elinewidth=1.3,capsize=1.5,color='dimgrey')


fig3, ax3 = plt.subplots(figsize=(11,5))
plt.subplots_adjust(left=0.07,right=0.75,top=0.95)

fig4, ax4 = plt.subplots(figsize=(11,5))
plt.subplots_adjust(left=0.07,right=0.75,top=0.95)
ax4.errorbar([],[],([],[]),label="x-position resolution ",marker='s',elinewidth=1.3,capsize=1.5,color='dimgrey')
ax4.errorbar([],[],([],[]),label="y-position resolution",marker='s',markerfacecolor='none',linestyle='dashed',elinewidth=1.3,capsize=1.5,color='dimgrey')

fig5, ax5 = plt.subplots(figsize=(11,5))
plt.subplots_adjust(left=0.07,right=0.75,top=0.95)
ax5.errorbar([],[],([],[]),label="x-position mean ",marker='s',elinewidth=1.3,capsize=1.5,color='dimgrey')
ax5.errorbar([],[],([],[]),label="y-position mean",marker='s',markerfacecolor='none',linestyle='dashed',elinewidth=1.3,capsize=1.5,color='dimgrey')


for file_path_list,label,chip,binary_resolution,color in zip(file_path_list_list,label_list,chip_list,binary_resolution_list,color_list):

   eff_list = []
   err_eff_up_x = []
   err_eff_low_x = []

   fit_list_x = []
   fit_list_y = []
   fit_list_x = []
   fit_list_y = []


   res_list_x = []
   err_res_up_x = []
   err_res_low_x = []
   res_list_y = []
   err_res_up_y = []
   err_res_low_y = []
   mean_list_x = []
   err_mean_up_x = []
   err_mean_low_x = []
   mean_list_y = []
   err_mean_up_y = []
   err_mean_low_y = []
   charge = []
   clustersize = []
   err_clustersize = []
   for file_path,thr in zip(file_path_list,thr_list):
      input_file = ROOT.TFile(file_path,"read")

      if label == "25um (June)":
         residualsX= input_file.Get("AnalysisDUT/APTS_4/local_residuals/residualsX")
         residualsY= input_file.Get("AnalysisDUT/APTS_4/local_residuals/residualsY")
         clusterSize= input_file.Get("AnalysisDUT/APTS_4/clusterSizeAssociated")
      else:
         residualsX= input_file.Get("AnalysisDUT/APTS_3/local_residuals/residualsX")
         residualsY= input_file.Get("AnalysisDUT/APTS_3/local_residuals/residualsY")
         clusterSize= input_file.Get("AnalysisDUT/APTS_3/clusterSizeAssociated")
         efficiency = input_file.Get("AnalysisEfficiency/APTS_3/eTotalEfficiency")

      eff_list.append(100*efficiency.GetEfficiency(1))
      err_eff_up_x.append(100*efficiency.GetEfficiencyErrorUp(1))
      err_eff_low_x.append(100*efficiency.GetEfficiencyErrorLow(1))


      residualsX.Rebin(10)
      residualsY.Rebin(10)

      func = ROOT.TF1("gauss","gaus(0)",-100,100)
      func.SetParameter(1,0)
      func.SetParameter(2,binary_resolution)
      
      residualsX.Fit(func,"QMR")
      if residualsX.GetStdDev()**2-tracking_resolution**2 > 0:
         res_list_x.append(math.sqrt(residualsX.GetStdDev()**2-tracking_resolution**2))
         fit_list_x.append(math.sqrt(func.GetParameter(2)**2-tracking_resolution**2))
         #res_list_x.append(math.sqrt(func.GetParameter(2)**2-tracking_resolution**2))
      else:
         res_list_x.append(0)
      err_res_up_x.append(residualsX.GetStdDevError())
      err_res_low_x.append(residualsX.GetStdDevError())
      mean_list_x.append(residualsX.GetMean())
      err_mean_up_x.append(residualsX.GetMeanError())
      err_mean_low_x.append(residualsX.GetMeanError())

      residualsY.Fit(func,"QMR")
      if residualsY.GetStdDev()**2-tracking_resolution**2 > 0:
         res_list_y.append(math.sqrt(residualsY.GetStdDev()**2-tracking_resolution**2))
         fit_list_y.append(math.sqrt(func.GetParameter(2)**2-tracking_resolution**2))
         #res_list_y.append(math.sqrt(func.GetParameter(2)**2-tracking_resolution**2))
      else:
         res_list_y.append(0)
      err_res_up_y.append(residualsY.GetStdDevError())
      err_res_low_y.append(residualsY.GetStdDevError())

      mean_list_y.append(residualsY.GetMean())
      err_mean_up_y.append(residualsY.GetMeanError())
      err_mean_low_y.append(residualsY.GetMeanError())

      charge.append(100*thr/hundredElectronToADCu[chip])
      clustersize.append(clusterSize.GetMean())
      err_clustersize.append(clusterSize.GetMeanError())
      del func
   print(res_list_x)
   print(res_list_y)
   print(fit_list_x)
   print(fit_list_y)
   asymmetric_error_x = [err_res_low_x, err_res_up_x]
   ax1.errorbar(charge, res_list_x, yerr=asymmetric_error_x, label=label, marker="s", linestyle='', color=color)

   asymmetric_error_y = [err_res_low_y, err_res_up_y]
   ax1.errorbar(charge, res_list_y, yerr=asymmetric_error_y, marker="s", linestyle='', color=color,markerfacecolor='none')

   asymmetric_error_y = [err_clustersize, err_clustersize]
   ax2.errorbar(charge, clustersize, yerr=asymmetric_error_y, marker="o", linestyle='', color=color,markerfacecolor='none')

   asymmetric_error_y = [err_eff_low_x, err_eff_up_x]
   ax3.errorbar(charge, eff_list, yerr=asymmetric_error_y, marker="o", linestyle='-', color=color,markerfacecolor='none', label=label)

   asymmetric_error_x = [err_res_low_x, err_res_up_x]
   ax4.errorbar(clustersize, res_list_x, yerr=asymmetric_error_x, label=label, marker="s", linestyle='', color=color)

   asymmetric_error_y = [err_res_low_y, err_res_up_y]
   ax4.errorbar(clustersize, res_list_y, yerr=asymmetric_error_y, marker="s", linestyle='', color=color,markerfacecolor='none')

   asymmetric_error_x = [err_mean_low_x, err_mean_up_x]
   ax5.errorbar(charge, mean_list_x, yerr=asymmetric_error_x, label=label, marker="s", linestyle='', color=color)

   asymmetric_error_y = [err_mean_low_y, err_mean_up_y]
   ax5.errorbar(charge, mean_list_y, yerr=asymmetric_error_y, marker="s", linestyle='', color=color,markerfacecolor='none')

x = 0.75
y = 0.95
x3 = 0.35
y3 = 0.30
ax3.set_ylabel('Efficiency (%)')
ax3.set_xlabel('Threshold (electrons)')
ax3.grid()
ax3.set_xlim(50,400)
ax3.set_ylim(69,101)
ax3.text(
    x3,y3,
    '$\\bf{ITS3}$ beam test WORK IN PROGRESS',
    fontsize=12,
    ha='center', va='top',
    transform=ax3.transAxes
)

ax3.text(
    x3,y3-0.06,
    '@SPS October 2022, 120 GeV/c protons and pions',
    fontsize=9,
    ha='center', va='top',
    transform=ax3.transAxes
)

ax3.text(1.1,1.0,
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
    transform=ax3.transAxes
    )
ax3.legend(loc='lower right',bbox_to_anchor =(1.35, -0.02),prop={"size":9})


ax3.axhline(99,linestyle='dashed',color='grey')
ax3.text(ax1.get_xlim()[0]-0.014*(ax1.get_xlim()[1]-ax1.get_xlim()[0]),99,"99",fontsize=7,ha='right', va='center')
fig3.savefig('efficiencyCheck'+suffix+'.png', dpi=600)
plt.show()


ax4.set_ylabel('Resolution (um)')
ax4.set_xlabel('Cluster size')
ax4.legend(loc='lower left')
ax4.grid()
fig4.savefig('resVsClustersize'+suffix+'.png', dpi=600)
plt.show()

ax5.set_ylabel('Mean (um)')
ax5.set_xlabel('Threshold (electrons)')
ax5.legend(loc='lower right',bbox_to_anchor =(1.35, -0.02),prop={"size":9})
ax5.grid()
fig5.savefig('meanVsThr'+suffix+'.png', dpi=600)
plt.show()


ax1.set_ylabel('Resolution (um)')
ax2.set_ylabel('Cluster size')
ax1.set_xlabel('Threshold (electrons)')
ax1.legend(loc='lower right')
ax1.grid()
#ax1.axhline(binary_resolution,linestyle='dashed',color='grey')
#ax1.text(170,15/math.sqrt(12),"Binary resolution",fontsize=10,ha='right', va='center')

ax2.set_ylim(1,3.5)
ax1.set_ylim(1,4.25)

ax1.legend(loc='lower right',bbox_to_anchor =(1.35, -0.02),prop={"size":9})

ax1.text(
    x,y,
    '$\\bf{ITS3}$ beam test WORK IN PROGRESS',
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

fig.savefig('resolutionVsThreshold'+suffix+'.png', dpi=600)
plt.show()


