from ROOT import TFile, TF1
import matplotlib as mpl
import matplotlib.pyplot as plt
import math
import argparse
import yaml
import os
import re

parser = argparse.ArgumentParser()
parser.add_argument('-fit', '--usefit', help='Use fit compute the resolution and mean', action='store_true')
parser.add_argument('-geo', '--geometric', help='Use geometric mean', action='store_true')
parser.add_argument("config", help="Path to the YAML configuration file")
args = parser.parse_args()


with open(os.path.expandvars(args.config), 'r') as stream:
    try:
        params = yaml.full_load(stream)
    except yaml.YAMLError as exc:
        print(exc)

use_fit = args.usefit
use_geometric = args.geometric

FILE_SUFFIX = params['FILE_SUFFIX']
CHIPS = params['CHIPS']
COLORS = params['COLORS']
LABELS = params['LABELS']
FILE_PATHS = params['FILE_PATHS']

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
tracking_resolution_x = 2.08
tracking_resolution_y = 2.08

#plot of the resolution (cluster size) vs thr
fig_resx_vs_thr, ax_resx_vs_thr = plt.subplots(figsize=(11,5))
plt.subplots_adjust(left=0.07,right=0.75,top=0.95)

ax_cluster_size_x = ax_resx_vs_thr.twinx()

ax_resx_vs_thr.errorbar([],[],([],[]),label="x-position resolution ",marker='s',elinewidth=1.3,capsize=1.5,color='dimgrey')
ax_resx_vs_thr.errorbar([],[],([],[]),label="cluster size",marker='o',markerfacecolor='none',linestyle='dashed',elinewidth=1.3,capsize=1.5,color='dimgrey')

fig_resy_vs_thr, ax_resy_vs_thr = plt.subplots(figsize=(11,5))
plt.subplots_adjust(left=0.07,right=0.75,top=0.95)

ax_cluster_size_y = ax_resy_vs_thr.twinx()

ax_resy_vs_thr.errorbar([],[],([],[]),label="y-position resolution",marker='s',linestyle='dashed',elinewidth=1.3,capsize=1.5,color='dimgrey')
ax_resy_vs_thr.errorbar([],[],([],[]),label="cluster size",marker='o',markerfacecolor='none',linestyle='dashed',elinewidth=1.3,capsize=1.5,color='dimgrey')

fig_resmean_vs_thr, ax_resmean_vs_thr = plt.subplots(figsize=(11,5))
plt.subplots_adjust(left=0.07,right=0.75,top=0.95)

ax_cluster_size_mean = ax_resmean_vs_thr.twinx()

ax_resmean_vs_thr.errorbar([],[],([],[]),label="resolution (geometric mean)",marker='s',linestyle='dashed',elinewidth=1.3,capsize=1.5,color='dimgrey')
ax_resmean_vs_thr.errorbar([],[],([],[]),label="cluster size",marker='o',markerfacecolor='none',linestyle='dashed',elinewidth=1.3,capsize=1.5,color='dimgrey')

#plot of the efficiency vs thr
fig_eff_vs_thr, ax_eff_vs_thr = plt.subplots(figsize=(11,5))
plt.subplots_adjust(left=0.07,right=0.75,top=0.95)

#plot of the resolution vs cluster size
fig_res_vs_clu, ax_res_vs_clu = plt.subplots(figsize=(11,5))
plt.subplots_adjust(left=0.07,right=0.75,top=0.95)
ax_res_vs_clu.errorbar([],[],([],[]),label="resolution (geometric mean)",marker='s',elinewidth=1.3,capsize=1.5,color='dimgrey')

#plot of the mean vs thr
fig_mean, ax_mean = plt.subplots(figsize=(11,5))
plt.subplots_adjust(left=0.07,right=0.75,top=0.95)
ax_mean.errorbar([],[],([],[]),label="x-position mean ",marker='s',elinewidth=1.3,capsize=1.5,color='dimgrey')
ax_mean.errorbar([],[],([],[]),label="y-position mean",marker='s',markerfacecolor='none',linestyle='dashed',elinewidth=1.3,capsize=1.5,color='dimgrey')

#plot of the efficiency vs cluster size
fig_eff_vs_clu, ax_eff_vs_clu = plt.subplots(figsize=(11,5))
plt.subplots_adjust(left=0.07,right=0.75,top=0.95)

for file_path_list,label,chip,color in zip(FILE_PATHS,LABELS,CHIPS,COLORS):

   file_path_list
   eff_list = []
   err_eff_up_x = []
   err_eff_low_x = []
   res_list_x = []
   err_res_up_x = []
   err_res_low_x = []
   res_list_y = []
   err_res_up_y = []
   err_res_low_y = []
   res_list_mean = []
   err_res_up_mean = []
   err_res_low_mean = []
   mean_list_x = []
   err_mean_up_x = []
   err_mean_low_x = []
   mean_list_y = []
   err_mean_up_y = []
   err_mean_low_y = []
   charge = []
   clustersize_list = []
   err_clustersize_list = []

   for file_path in file_path_list:
      thr = re.findall(r'\d+', file_path)[1]
      input_file = TFile(file_path,"read")

      residualsX= input_file.Get("AnalysisDUT/APTS_3/local_residuals/residualsX")
      residualsY= input_file.Get("AnalysisDUT/APTS_3/local_residuals/residualsY")
      clusterSize= input_file.Get("AnalysisDUT/APTS_3/clusterSizeAssociated")
      efficiency = input_file.Get("AnalysisEfficiency/APTS_3/eTotalEfficiency")

      eff_list.append(100*efficiency.GetEfficiency(1))
      err_eff_up_x.append(100*efficiency.GetEfficiencyErrorUp(1))
      err_eff_low_x.append(100*efficiency.GetEfficiencyErrorLow(1))
      charge.append(100*thr/hundredElectronToADCu[chip])

      residualsX.Rebin(10)
      residualsY.Rebin(10)

      if use_fit:
        func = TF1("gauss","gaus(0)",-100,100)
        func.SetParameter(1,0)
        func.SetParameter(2,3)
        residualsX.Fit(func,"QMR")
        res_x = math.sqrt(func.GetParameter(2)**2-tracking_resolution_x**2)
        err_res_x = func.GetParError(2)
        mean_x = func.GetParameter(1)
        err_mean_x = func.GetParError(1)
        residualsY.Fit(func,"QMR")
        res_y = math.sqrt(func.GetParameter(2)**2-tracking_resolution_y**2)
        err_res_y = func.GetParError(2)
        mean_y = func.GetParameter(1)
        err_mean_y = func.GetParError(1)
      else:
        res_x = math.sqrt(residualsX.GetStdDev()**2-tracking_resolution_x**2)
        res_y = math.sqrt(residualsY.GetStdDev()**2-tracking_resolution_y**2)
        err_res_x = residualsX.GetStdDevError()
        err_res_y = residualsY.GetStdDevError()
        mean_x = residualsX.GetMean()
        mean_y = residualsY.GetMean()
        err_mean_x = residualsX.GetMeanError()
        err_mean_y = residualsY.GetMeanError()

      #fill list with the resolutions
      mean_list_x.append(res_x)
      err_res_up_x.append(err_res_x)
      err_res_low_x.append(err_res_x)
      mean_list_y.append(res_y)
      err_res_up_x.append(err_res_x)
      err_res_low_x.append(err_res_x)
      #fill list with the mean values of the distributions
      mean_list_x.append(mean_x)
      mean_list_y.append(mean_y)
      err_mean_up_x.append(err_mean_x)
      err_mean_low_x.append(err_mean_x)
      err_mean_up_y.append(err_mean_y)
      err_mean_low_y.append(err_mean_y)
      
      #compute mean resolutiono and fill the list 
      if use_geometric:
        res_list_mean.append(math.sqrt(res_x*res_y))
        err_mean = math.sqrt(res_x/res_y*err_res_y**2+res_y/res_x*err_res_x**2)
      else:
        res_list_mean.append((res_x+res_y)/2.)
        err_mean = math.sqrt(err_res_x**2+err_res_y**2)/2.
      
      err_res_up_mean.append(err_mean)
      err_res_low_mean.append(err_mean)
      
      #fill list with the cluster size
      clustersize_list.append(clusterSize.GetMean())
      err_clustersize_list.append(clusterSize.GetMeanError())

      del func

   asymmetric_error_x = [err_res_low_x, err_res_up_x]
   ax_resx_vs_thr.errorbar(charge, res_list_x, yerr=asymmetric_error_x, label=label, marker="s", linestyle='', color=color)

   asymmetric_error_y = [err_res_low_y, err_res_up_y]
   ax_resy_vs_thr.errorbar(charge, res_list_y, yerr=asymmetric_error_y, label=label, marker="s", linestyle='', color=color)

   asymmetric_error_y = [err_res_low_mean, err_res_up_mean]
   ax_resmean_vs_thr.errorbar(charge, res_list_mean, yerr=asymmetric_error_y, label=label, marker="s", linestyle='', color=color)

   asymmetric_error_y = [err_clustersize_list, err_clustersize_list]
   ax_cluster_size_y.errorbar(charge, clustersize_list, yerr=asymmetric_error_y, marker="o", linestyle='', color=color,markerfacecolor='none')

   asymmetric_error_y = [err_clustersize_list, err_clustersize_list]
   ax_cluster_size_y.errorbar(charge, clustersize_list, yerr=asymmetric_error_y, marker="o", linestyle='', color=color,markerfacecolor='none')

   asymmetric_error_y = [err_clustersize_list, err_clustersize_list]
   ax_cluster_size_mean.errorbar(charge, clustersize_list, yerr=asymmetric_error_y, marker="o", linestyle='', color=color,markerfacecolor='none')

   asymmetric_error_y = [err_eff_low_x, err_eff_up_x]
   ax_eff_vs_thr.errorbar(charge, eff_list, yerr=asymmetric_error_y, marker="o", linestyle='-', color=color,markerfacecolor='none', label=label)

   asymmetric_error_x = [err_res_low_mean, err_res_up_mean]
   ax_res_vs_clu.errorbar(clustersize_list, res_list_mean, yerr=asymmetric_error_x, label=label, marker="s", linestyle='', color=color)

   asymmetric_error_x = [err_mean_low_x, err_mean_up_x]
   ax_mean.errorbar(charge, mean_list_x, yerr=asymmetric_error_x, label=label, marker="s", linestyle='', color=color)

   asymmetric_error_y = [err_mean_low_y, err_mean_up_y]
   ax_mean.errorbar(charge, mean_list_y, yerr=asymmetric_error_y, marker="s", linestyle='', color=color,markerfacecolor='none')

   asymmetric_error_y = [err_eff_low_x, err_eff_up_x]
   ax_eff_vs_clu.errorbar(clustersize_list, eff_list, yerr=asymmetric_error_y, marker="s", label=label, linestyle='', color=color,markerfacecolor='none')

x = 0.75
y = 0.95
x3 = 0.35
y3 = 0.30
ax_eff_vs_thr.set_ylabel('Efficiency (%)')
ax_eff_vs_thr.set_xlabel('Threshold (electrons)')
ax_eff_vs_thr.grid()
ax_eff_vs_thr.set_xlim(50,400)
ax_eff_vs_thr.set_ylim(69,101)
ax_eff_vs_thr.text(
    x3,y3,
    '$\\bf{ITS3}$ beam test WORK IN PROGRESS',
    fontsize=12,
    ha='center', va='top',
    transform=ax_eff_vs_thr.transAxes
)

ax_eff_vs_thr.text(
    x3,y3-0.06,
    '@SPS October 2022, 120 GeV/c protons and pions',
    fontsize=9,
    ha='center', va='top',
    transform=ax_eff_vs_thr.transAxes
)

ax_eff_vs_thr.text(1.1,1.0,
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
    transform=ax_eff_vs_thr.transAxes
    )
ax_eff_vs_thr.legend(loc='lower right',bbox_to_anchor =(1.35, -0.02),prop={"size":9})


ax_eff_vs_thr.axhline(99,linestyle='dashed',color='grey')
ax_eff_vs_thr.text(ax_resx_vs_thr.get_xlim()[0]-0.014*(ax_resx_vs_thr.get_xlim()[1]-ax_resx_vs_thr.get_xlim()[0]),99,"99",fontsize=7,ha='right', va='center')
fig_eff_vs_thr.savefig('efficiencyCheck'+FILE_SUFFIX+'.png', dpi=600)

ax_res_vs_clu.set_ylabel('Resolution (um)')
ax_res_vs_clu.set_xlabel('Cluster size')
ax_res_vs_clu.legend(loc='lower right',bbox_to_anchor =(1.35, -0.02),prop={"size":9})
ax_res_vs_clu.grid()

ax_res_vs_clu.text(
    x,y,
    '$\\bf{ITS3}$ beam test WORK IN PROGRESS',
    fontsize=12,
    ha='center', va='top',
    transform=ax_res_vs_clu.transAxes
)

ax_res_vs_clu.text(
    x,y-0.06,
    '@SPS October 2022, 120 GeV/c protons and pions',
    fontsize=9,
    ha='center', va='top',
    transform=ax_res_vs_clu.transAxes
)

ax_res_vs_clu.text(1.1,1.0,
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
    transform=ax_res_vs_clu.transAxes
    )

fig_res_vs_clu.savefig('resVsClustersize_list'+FILE_SUFFIX+'.png', dpi=600)


ax_mean.set_ylabel('Mean (um)')
ax_mean.set_xlabel('Threshold (electrons)')
ax_mean.legend(loc='lower right',bbox_to_anchor =(1.35, -0.02),prop={"size":9})
ax_mean.grid()
fig_mean.savefig('meanVsThr'+FILE_SUFFIX+'.png', dpi=600)



ax_resx_vs_thr.set_ylabel('Resolution (um)')
ax_cluster_size_x.set_ylabel('Cluster size')
ax_resx_vs_thr.set_xlabel('Threshold (electrons)')
ax_resx_vs_thr.legend(loc='lower right')
ax_resx_vs_thr.grid()

ax_resy_vs_thr.set_ylabel('Resolution (um)')
ax_cluster_size_y.set_ylabel('Cluster size')
ax_resy_vs_thr.set_xlabel('Threshold (electrons)')
ax_resy_vs_thr.legend(loc='lower right')
ax_resy_vs_thr.grid()

ax_resmean_vs_thr.set_ylabel('Resolution (um)')
ax_cluster_size_mean.set_ylabel('Cluster size')
ax_resmean_vs_thr.set_xlabel('Threshold (electrons)')
ax_resmean_vs_thr.legend(loc='lower right')
ax_resmean_vs_thr.grid()

ax_eff_vs_clu.set_ylabel('Efficiency (%)')
ax_eff_vs_clu.set_xlabel('Cluster size')
ax_eff_vs_clu.grid()
ax_eff_vs_clu.legend(loc='lower right',bbox_to_anchor =(1.35, -0.02),prop={"size":9})

fig_eff_vs_clu.savefig('efficiencyVsClustersize_list'+FILE_SUFFIX+'.png', dpi=600)

ax_cluster_size_x.set_ylim(1,3.5)
ax_resx_vs_thr.set_ylim(1,4.25)

ax_resx_vs_thr.legend(loc='lower right',bbox_to_anchor =(1.35, -0.02),prop={"size":9})

ax_resx_vs_thr.text(
    x,y,
    '$\\bf{ITS3}$ beam test WORK IN PROGRESS',
    fontsize=12,
    ha='center', va='top',
    transform=ax_resx_vs_thr.transAxes
)

ax_resx_vs_thr.text(
    x,y-0.06,
    '@SPS October 2022, 120 GeV/c protons and pions',
    fontsize=9,
    ha='center', va='top',
    transform=ax_resx_vs_thr.transAxes
)

ax_resx_vs_thr.text(1.1,1.0,
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
    transform=ax_resx_vs_thr.transAxes
    )

ax_cluster_size_y.set_ylim(1,3.5)
ax_resy_vs_thr.set_ylim(1,4.25)

ax_resy_vs_thr.legend(loc='lower right',bbox_to_anchor =(1.35, -0.02),prop={"size":9})

ax_resy_vs_thr.text(
    x,y,
    '$\\bf{ITS3}$ beam test WORK IN PROGRESS',
    fontsize=12,
    ha='center', va='top',
    transform=ax_resy_vs_thr.transAxes
)

ax_resy_vs_thr.text(
    x,y-0.06,
    '@SPS October 2022, 120 GeV/c protons and pions',
    fontsize=9,
    ha='center', va='top',
    transform=ax_resy_vs_thr.transAxes
)

ax_resy_vs_thr.text(1.1,1.0,
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
    transform=ax_resy_vs_thr.transAxes
    )
ax_cluster_size_x_3.set_ylim(1,3.5)
ax_resmean_vs_thr.set_ylim(1,4.25)

ax_resmean_vs_thr.legend(loc='lower right',bbox_to_anchor =(1.35, -0.02),prop={"size":9})

ax_resmean_vs_thr.text(
    x,y,
    '$\\bf{ITS3}$ beam test WORK IN PROGRESS',
    fontsize=12,
    ha='center', va='top',
    transform=ax_resmean_vs_thr.transAxes
)

ax_resmean_vs_thr.text(
    x,y-0.06,
    '@SPS October 2022, 120 GeV/c protons and pions',
    fontsize=9,
    ha='center', va='top',
    transform=ax_resmean_vs_thr.transAxes
)

ax_resmean_vs_thr.text(1.1,1.0,
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
    transform=ax_resmean_vs_thr.transAxes
    )
   
fig_resx_vs_thr.savefig('resolutionVsThreshold_x'+FILE_SUFFIX+'.png', dpi=600)
fig_resy_vs_thr.savefig('resolutionVsThreshold_y'+FILE_SUFFIX+'.png', dpi=600)
fig_resmean_vs_thr.savefig('resolutionVsThreshold_mean'+FILE_SUFFIX+'.png', dpi=600)