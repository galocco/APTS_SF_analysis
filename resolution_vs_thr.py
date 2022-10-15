import ROOT
import matplotlib as mpl
import matplotlib.pyplot as plt
#from ROOT import TCanvas
#dictionary with the conversion from 100e- to ADCu
hundredElectronToADCu = {
               "AF15_W13_1.2V" : 113.5602885,
               "AF15_W22_1.2V" : 112.6764784,
               "AF15B_W22_1.2V":  79.90360556,
               "AF15P_W22_1.2V":  79.82152217,
               "AF10P_W22_1.2V":  80.31095738,
               "AF20P_W22_1.2V":  80.09704306,
               "AF25P_W22_1.2V":  79.86636469,
               "AF15P_W22_0V"  :  44.7844201,
               "AF15P_W22_2.4V": 103.97717,
               "AF15P_W22_3.6V": 116.4895804,
               "AF15P_W22_4.8V": 122.3611669
            }

#list of the analysis results path
#file_path_list = ["alignment_414153944221013153949_DUT_cut60_3.root"]
file_path_list = ["alignment_415000658221014000702_DUT_cut60_3.root"]#jobsub.alignDUT_cut60_3_run

#list of the chips
chip_list = ["AF15P_W22_1.2V"]
#list of the labels for the plot
#label_list = ["Irradiated 10^15"]
label_list = ["pixel pitch = 10 um"]

color_list = ['b', 'black', 'g', 'r']

hist = []
fig, ax1 = plt.subplots(figsize=(11,5))
plt.subplots_adjust(left=0.07,right=0.75,top=0.95)

fig2, ax2 = plt.subplots(figsize=(11,5))
plt.subplots_adjust(left=0.07,right=0.75,top=0.95)

thr_list = [60,80,100,120,140,160,180,200,250,300,350,500,600,700]

for file_path,label,chip,color in zip(file_path_list,label_list,chip_list,color_list):
   input_file = ROOT.TFile(file_path,"read")

   if label == "25um (June)":
      residualsX= input_file.Get("AnalysisDUT/APTS_4/local_residuals/residualsXVsSeedCharge")
      residualsY= input_file.Get("AnalysisDUT/APTS_4/local_residuals/residualsYVsSeedCharge")
   else:
      residualsX= input_file.Get("AnalysisDUT/APTS_3/local_residuals/residualsXVsSeedCharge")
      residualsY= input_file.Get("AnalysisDUT/APTS_3/local_residuals/residualsYVsSeedCharge")
   
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

   for thr in thr_list:
      thr_bin = residualsY.GetYaxis().FindBin(thr)
      projX = residualsX.ProjectionX("x", thr_bin)
      projY = residualsY.ProjectionX("y", thr_bin)

      func = ROOT.TF1("gauss","gaus(0)",-100,100)
      func.SetParameter(1,0)
      func.SetParameter(2,3)
      projX.Fit(func,"QMR")
      res_list_x.append(func.GetParameter(2))
      err_res_up_x.append(func.GetParError(2))
      err_res_low_x.append(func.GetParError(2))
      mean_list_x.append(func.GetParameter(1))
      err_mean_up_x.append(func.GetParError(1))
      err_mean_low_x.append(func.GetParError(1))

      projY.Fit(func,"QMR")
      res_list_y.append(func.GetParameter(2))
      err_res_up_y.append(func.GetParError(2))
      err_res_low_y.append(func.GetParError(2))

      mean_list_y.append(func.GetParameter(1))
      err_mean_up_y.append(func.GetParError(1))
      err_mean_low_y.append(func.GetParError(1))

      charge.append(100*thr/hundredElectronToADCu[chip])
      del func

   labelX = label + " X"
   asymmetric_error_x = [err_res_low_x, err_res_up_x]
   ax1.errorbar(charge, res_list_x, yerr=asymmetric_error_x, label=labelX, marker="s", linestyle='', color=color)

   labelY = label + " Y"
   asymmetric_error_y = [err_res_low_y, err_res_up_y]
   ax1.errorbar(charge, res_list_y, yerr=asymmetric_error_y, label=labelY, marker="s", linestyle='', color='g')

   labelX = label + " X"
   asymmetric_error_x = [err_mean_low_x, err_mean_up_x]
   ax2.errorbar(charge, mean_list_x, yerr=asymmetric_error_x, label=labelX, marker="s", linestyle='', color=color)

   labelY = label + " Y"
   asymmetric_error_y = [err_mean_low_y, err_mean_up_y]
   ax2.errorbar(charge, mean_list_y, yerr=asymmetric_error_y, label=labelY, marker="s", linestyle='', color='g')

ax1.set_ylabel('Resolution (um)')
ax1.set_xlabel('Threshold (electrons)')
ax1.legend(loc='lower left')
ax1.grid()
ax1.set_ylim(2,3.5)

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

fig.savefig('resolutionVsThreshold_10P.png', dpi=600)
plt.show()


ax2.set_ylabel('Mean (um)')
ax2.set_xlabel('Threshold (electrons)')
ax2.legend(loc='lower left')
ax2.grid()
ax2.set_ylim(-1,1)

ax2.legend(loc='lower right',bbox_to_anchor =(1.32, -0.02),prop={"size":9})

x = 0.8
y = 0.95

ax2.text(
    x,y,
    '$\\bf{ITS3}$ beam test $\\it{preliminary}$',
    fontsize=12,
    ha='center', va='top',
    transform=ax2.transAxes
)

ax2.text(
    x,y-0.06,
    '@SPS October 2022, 120 GeV/c protons and pions',
    fontsize=9,
    ha='center', va='top',
    transform=ax2.transAxes
)

ax2.text(1.1,1.0,
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
    transform=ax2.transAxes
    )

fig2.savefig('meanVsThreshold_10P.png', dpi=600)
plt.show()
