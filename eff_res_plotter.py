from ROOT import TFile, TF1, TMath
import matplotlib as mpl
import matplotlib.pyplot as plt
import math
import argparse
import yaml
import os
import re


def qGauss(x, par):
    if x[0] <= par[4]:
        fitval = par[0]*TMath.Power(1 - (1 - par[2])*(1./(3 - par[2]))*(
            x[0] - par[4])*(x[0] - par[4])/(par[1]*par[1]), 1./(1 - par[2]))
    else:
        fitval = par[0]*TMath.Power(1 - (1 - par[3])*(1./(3 - par[3]))*(
            x[0] - par[4])*(x[0] - par[4])/(par[1]*par[1]), 1./(1 - par[3]))
    return fitval


def gauss_exp_tails(x, par):
    N = par[0]
    sig = par[1]
    mu = par[4]
    tau0 = par[2]
    tau1 = par[3]
    u = (x[0] - mu) / sig
    if (u < tau0):
        return N*TMath.Exp(-tau0 * (u - 0.5 * tau0))
    elif (u <= tau1):
        return N*TMath.Exp(-u * u * 0.5)
    else:
        return N*TMath.Exp(-tau1 * (u - 0.5 * tau1))


parser = argparse.ArgumentParser()
parser.add_argument(
    '-f', '--usefit', help='Use fit compute the resolution and mean', action='store_true')
parser.add_argument('-q', '--useqgauss',
                    help='Perform qGaussian fit', action='store_true')
parser.add_argument('-e', '--useexpgaus',
                    help='Perform gaussian fit with exponential tails', action='store_true')
parser.add_argument('-l', '--limit',
                    help='Apply lower limit of e- range', action='store_true')
parser.add_argument('-geo', '--geometric',
                    help='Use geometric mean', action='store_true')
parser.add_argument("config", help="Path to the YAML configuration file")
args = parser.parse_args()

with open(os.path.expandvars(args.config), 'r') as stream:
    try:
        params = yaml.full_load(stream)
    except yaml.YAMLError as exc:
        print(exc)

use_fit = args.usefit
use_qGaussian = args.useqgauss
use_exp_gaussian = args.useexpgaus
use_limit = args.limit

if use_qGaussian and use_exp_gaussian:
    print("ATTENTION: both qGaussian and gaussian with exp-tails are selected")
    use_exp_gaussian = False
if use_fit:
    fit_label = "fit"
else:
    fit_label = "rms"

use_geometric = args.geometric
if use_geometric:
    mean_label = "geometric"
else:
    mean_label = "arithmetic"

FILE_SUFFIX = params['FILE_SUFFIX']
CHIPS = params['CHIPS']
COLORS = params['COLORS']
LABELS = params['LABELS']
FILE_PATHS = params['FILE_PATHS']
STATUS = '$\\bf{ITS3}$ beam test '+params['STATUS']
TEST_BEAM = ''
for TEST in params['TEST_BEAMS']:
    TEST_BEAM += TEST + "\n"
NOISE_PATHS = params['NOISE_PATHS']
NSIGMANOISE = params['NSIGMANOISE']
if NSIGMANOISE ==0:
    NOISE_PATHS = [None] * len(FILE_PATHS)
CHIP_SETTINGS = '\n'.join([
    '$\\bf{%s}$' % 'APTS\ SF',
    #'type: %s'%'modified with gap',
    'split:  %s' % '4',
    #'$V_{sub}=V_{pwell}$ = -1.2 V',
    '$I_{reset}=%s\,\\mathrm{pA}$' % 100,
    '$I_{biasn}=%s\,\\mathrm{\mu A}$' % 5,
    '$I_{biasp}=%s\,\\mathrm{\mu A}$' % 0.5,
    '$I_{bias4}=%s\,\\mathrm{\mu A}$' % 150,
    '$I_{bias3}=%s\,\\mathrm{\mu A}$' % 200,
    '$V_{reset}=%s\,\\mathrm{mV}$' % 500
])
plots_dir = "plots/"+FILE_SUFFIX
if not os.path.isdir(plots_dir):
    os.mkdir(plots_dir)

# dictionary with the conversion from 100e- to ADCu
hundredElectronToADCu = {
                            "AF15_W13_1.2V":  113.5602885,
                            "AF15_W22_1.2V": 112.6764784,
                            "AF15_W22_0.0V":	99.96019279,
                            "AF15_W22_2.4V":	118.6366722,
                            "AF15_W22_3.6V":	122.4966069,
                            "AF15_W22_4.8V":	124.5837159,
                            "AF15B_W22_1.2V":	79.90360556,
                            "AF15B_W22_0.0V":	44.38443415,
                            "AF15B_W22_2.4V":	104.1295414,
                            "AF25B_W22_1.2V":79.19905893,				
                            "AF10B_W22_1.2V":78.24761423,				
                            "AF15P_W22_1.2V": 79.82152217,
                            "AF10P_W22_1.2V":	80.31095738,
                            "AF20P_W22_1.2V":		80.09704306,
                            "AF25P_W22_1.2V":		79.86636469,
                            "AF15P_W22_0V": 44.7844201,
                            "AF15P_W22_2.4V": 103.97717,
                            "AF15P_W22_3.6V": 116.4895804,
                            "AF15P_W22_4.8V": 122.3611669,
                                        
                            "AF15P_W22B9_IR2.5_1.2V":	76.7774608,
                            "AF15P_W22B12_IR2.5_1.2V": 76.25865981,
                            "AF15P_W22B16_IR2.5_1.2V": 81.95167308,
                            "AF15P_W22B16_IR2.5_0.0V": 48.42682102,
                            "AF15P_W22B16_IR2.5_2.4V": 100.5220934,
                            "AF15P_W22B16_IR2.5_3.6V": 110.0892196,
                            "AF15P_W22B16_IR2.5_4.8V": 114.0137095,
                        }

# tracking resolution from telescope-optimizer
tracking_resolution_x_SPS = 2.08
tracking_resolution_y_SPS = 2.08
tracking_resolution_x_PSJune = 3.15
tracking_resolution_y_PSJune = 3.15
tracking_resolution_x_PSAugust = 2.85 #2.43 
tracking_resolution_y_PSAugust = 2.85 #2.43 


# plot of the resolution (Average cluster size) vs thr
fig_resx_vs_thr, ax_resx_vs_thr = plt.subplots(figsize=(11, 5))
plt.subplots_adjust(left=0.07, right=0.75, top=0.95)

ax_cluster_size_x = ax_resx_vs_thr.twinx()

ax_resx_vs_thr.errorbar([], [], ([], []), label="x-position resolution ",
                        marker='s', elinewidth=1.3, capsize=1.5, color='dimgrey')
ax_resx_vs_thr.errorbar([], [], ([], []), label="Average cluster size", marker='o',
                        markerfacecolor='none', linestyle='dashed', elinewidth=1.3, capsize=1.5, color='dimgrey')

fig_resy_vs_thr, ax_resy_vs_thr = plt.subplots(figsize=(11, 5))
plt.subplots_adjust(left=0.07, right=0.75, top=0.95)

ax_cluster_size_y = ax_resy_vs_thr.twinx()

ax_resy_vs_thr.errorbar([], [], ([], []), label="y-position resolution",
                        marker='s', linestyle='dashed', elinewidth=1.3, capsize=1.5, color='dimgrey')
ax_resy_vs_thr.errorbar([], [], ([], []), label="Average cluster size", marker='o',
                        markerfacecolor='none', linestyle='dashed', elinewidth=1.3, capsize=1.5, color='dimgrey')

fig_resmean_vs_thr, ax_resmean_vs_thr = plt.subplots(figsize=(11, 5))
plt.subplots_adjust(left=0.07, right=0.75, top=0.95)

ax_cluster_size_mean = ax_resmean_vs_thr.twinx()

ax_resmean_vs_thr.errorbar([], [], ([], []), label="resolution ("+mean_label+" mean)",
                           marker='s', linestyle='dashed', elinewidth=1.3, capsize=1.5, color='dimgrey')
ax_resmean_vs_thr.errorbar([], [], ([], []), label="Average cluster size", marker='o',
                           markerfacecolor='none', linestyle='dashed', elinewidth=1.3, capsize=1.5, color='dimgrey')

# plot of the efficiency vs thr
fig_eff_vs_thr, ax_eff_vs_thr = plt.subplots(figsize=(11, 5))
plt.subplots_adjust(left=0.07, right=0.75, top=0.95)
ax_eff_vs_thr.errorbar([], [], ([], []), label="Efficiency", marker='o',
                       linestyle='dashed', elinewidth=1.3, capsize=1.5, color='dimgrey')


# plot of the resolution vs Average cluster size
fig_res_vs_clu, ax_res_vs_clu = plt.subplots(figsize=(11, 5))
plt.subplots_adjust(left=0.07, right=0.75, top=0.95)
ax_res_vs_clu.errorbar([], [], ([], []), label="resolution ("+mean_label+" mean)",
                       marker='s', elinewidth=1.3, capsize=1.5, color='dimgrey')

# plot of the mean vs thr
fig_mean, ax_mean = plt.subplots(figsize=(11, 5))
plt.subplots_adjust(left=0.07, right=0.75, top=0.95)
ax_mean.errorbar([], [], ([], []), label="x-position mean ",
                 marker='s', elinewidth=1.3, capsize=1.5, color='dimgrey')
ax_mean.errorbar([], [], ([], []), label="y-position mean", marker='s',
                 markerfacecolor='none', linestyle='dashed', elinewidth=1.3, capsize=1.5, color='dimgrey')

# plot of the efficiency vs Average cluster size
fig_eff_vs_clu, ax_eff_vs_clu = plt.subplots(figsize=(11, 5))
plt.subplots_adjust(left=0.07, right=0.75, top=0.95)
fit_info = TFile(plots_dir+"/fit_info.root", "recreate")

for file_path_list, noise_path, label, chip, color in zip(FILE_PATHS, NOISE_PATHS, LABELS, CHIPS, COLORS):
    sub_dir = fit_info.mkdir(label)
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
    
    if chip == "AF25P_W22_1.2V" or "June" in label:
        apts = "4"
    else:
        apts = "3"


    eThrLimit = 0
    if use_limit and NSIGMANOISE>0:
        noise_file = TFile(noise_path, "read")
        noise_values = noise_file.Get(
            "EventLoaderEUDAQ2/APTS_"+apts+"/hPixelRawValues")
        eThrLimit = (noise_values.GetStdDev()*NSIGMANOISE)*100/hundredElectronToADCu[chip]
        print("plotting above ",eThrLimit," electrons")
        noise_file.Close()

    for file_path in file_path_list:
        print(file_path)
        thr = int(re.findall(r'\d+', file_path)[-1])
        if thr*100/hundredElectronToADCu[chip] < eThrLimit:
            continue
        input_file = TFile(file_path, "read")

        residualsX = input_file.Get(
            "AnalysisDUT/APTS_"+apts+"/local_residuals/residualsX")
        residualsY = input_file.Get(
            "AnalysisDUT/APTS_"+apts+"/local_residuals/residualsY")
        clusterSize = input_file.Get(
            "AnalysisDUT/APTS_"+apts+"/clusterSizeAssociated")
        efficiency = input_file.Get(
            "AnalysisEfficiency/APTS_"+apts+"/eTotalEfficiency")

        eff_list.append(100*efficiency.GetEfficiency(1))
        err_eff_up_x.append(100*efficiency.GetEfficiencyErrorUp(1))
        err_eff_low_x.append(100*efficiency.GetEfficiencyErrorLow(1))
        charge.append(100*thr/hundredElectronToADCu[chip])

        residualsX.Rebin(4)
        residualsY.Rebin(4)
        if chip == "AF20P_W22_1.2V":
            if "June" in label:
                tracking_resolution_x = tracking_resolution_x_PSJune
                tracking_resolution_y = tracking_resolution_y_PSJune
                print("june")
            else:
                tracking_resolution_x = tracking_resolution_x_PSAugust
                tracking_resolution_y = tracking_resolution_y_PSAugust
        else:
            tracking_resolution_x = tracking_resolution_x_SPS
            tracking_resolution_y = tracking_resolution_y_SPS

        if use_fit:
            sub_dir.cd()
            mean_par = 4
            sigma_par = 1
            if use_qGaussian:
                func = TF1("qGauss", qGauss, -40, 40, 5)
                func.SetParameter(0, 10)
                func.SetParLimits(0, 0.1, 10000)
                func.SetParameter(1, 3)
                func.SetParLimits(1, 2.5, 8)
                func.SetParameter(2, 1.1)
                func.SetParLimits(2, 1.0005, 5)
                func.SetParameter(3, 1.1)
                func.SetParLimits(3, 1.0005, 5)
                func.SetParameter(4, 0)
                func.SetParLimits(4, -1, 1)
            elif use_exp_gaussian:
                func = TF1("qGauss", gauss_exp_tails, -40, 40, 5)
                func.SetParameter(0, 700)
                func.SetParLimits(0, 1, 10000)
                func.SetParameter(1, 4)
                func.SetParLimits(1, 2.5, 8)
                func.SetParameter(2, -20)
                func.SetParLimits(2, -100, 0)
                func.SetParameter(3, 20)
                func.SetParLimits(3, 0, 100)
                # func.FixParameter(4,0)
                func.SetParameter(4, 0)
                func.SetParLimits(4, -1, 1)
            else:
                func = TF1("qGauss", "gaus(0)", -40, 40, 5)

                func.SetParameter(1, 0)
                func.SetParameter(2, 4)
                func.SetParLimits(2, 2.5, 8)
                mean_par = 1
                sigma_par = 2

            # func.SetParameter(2,3)
            residualsX.Fit(func, "QMR+")
            #test = 0
            # input(test)

            res_x = math.sqrt(func.GetParameter(sigma_par)
                              ** 2-tracking_resolution_x**2)

            err_res_x = func.GetParError(sigma_par)
            mean_x = func.GetParameter(mean_par)
            err_mean_x = func.GetParError(mean_par)
            residualsY.Fit(func, "QMR+")
            res_y = math.sqrt(func.GetParameter(sigma_par)
                              ** 2-tracking_resolution_y**2)
            err_res_y = func.GetParError(sigma_par)
            mean_y = func.GetParameter(mean_par)
            err_mean_y = func.GetParError(mean_par)

            residualsX.SetName('residualsX_'+chip+'_thr_'+str(thr))
            residualsY.SetName('residualsY_'+chip+'_thr_'+str(thr))
            residualsX.Write()
            residualsY.Write()
        else:
            if residualsX.GetStdDev() **2-tracking_resolution_x**2 >0:
                res_x = math.sqrt(residualsX.GetStdDev() **
                                2-tracking_resolution_x**2)
                res_y = math.sqrt(residualsY.GetStdDev() **
                                2-tracking_resolution_y**2)
            else:
                print(residualsX.GetStdDev() **2-tracking_resolution_x**2)
                print(residualsX.GetStdDev())
                print(tracking_resolution_x)
                res_x = 0
                res_y = 0
            err_res_x = residualsX.GetStdDevError()
            err_res_y = residualsY.GetStdDevError()
            mean_x = residualsX.GetMean()
            mean_y = residualsY.GetMean()
            err_mean_x = residualsX.GetMeanError()
            err_mean_y = residualsY.GetMeanError()

        # fill list with the resolutions
        res_list_x.append(res_x)
        err_res_up_x.append(err_res_x)
        err_res_low_x.append(err_res_x)
        res_list_y.append(res_y)
        err_res_up_y.append(err_res_y)
        err_res_low_y.append(err_res_y)
        # fill list with the mean values of the distributions
        mean_list_x.append(mean_x)
        mean_list_y.append(mean_y)
        err_mean_up_x.append(err_mean_x)
        err_mean_low_x.append(err_mean_x)
        err_mean_up_y.append(err_mean_y)
        err_mean_low_y.append(err_mean_y)

        # compute mean resolutiono and fill the list
        if use_geometric:
            res_list_mean.append(math.sqrt(res_x*res_y))
            err_mean = math.sqrt(res_x/res_y*err_res_y **
                                 2+res_y/res_x*err_res_x**2)
        else:
            res_list_mean.append((res_x+res_y)/2.)
            err_mean = math.sqrt(err_res_x**2+err_res_y**2)/2.

        err_res_up_mean.append(err_mean)
        err_res_low_mean.append(err_mean)

        # fill list with the Average cluster size
        clustersize_list.append(clusterSize.GetMean())
        err_clustersize_list.append(clusterSize.GetMeanError())

    asymmetric_error_x = [err_res_low_x, err_res_up_x]
    ax_resx_vs_thr.errorbar(charge, res_list_x, yerr=asymmetric_error_x,
                            label=label, marker="s", linestyle='', color=color)

    asymmetric_error_y = [err_res_low_y, err_res_up_y]
    ax_resy_vs_thr.errorbar(charge, res_list_y, yerr=asymmetric_error_y,
                            label=label, marker="s", linestyle='', color=color)

    asymmetric_error_y = [err_res_low_mean, err_res_up_mean]
    ax_resmean_vs_thr.errorbar(charge, res_list_mean, yerr=asymmetric_error_y,
                               label=label, marker="s", linestyle='', color=color)

    asymmetric_error_y = [err_clustersize_list, err_clustersize_list]
    ax_cluster_size_x.errorbar(charge, clustersize_list, yerr=asymmetric_error_y,
                               marker="o", linestyle='', color=color, markerfacecolor='none')

    asymmetric_error_y = [err_clustersize_list, err_clustersize_list]
    ax_cluster_size_y.errorbar(charge, clustersize_list, yerr=asymmetric_error_y,
                               marker="o", linestyle='', color=color, markerfacecolor='none')

    asymmetric_error_y = [err_clustersize_list, err_clustersize_list]
    ax_cluster_size_mean.errorbar(charge, clustersize_list, yerr=asymmetric_error_y,
                                  marker="o", linestyle='', color=color, markerfacecolor='none')

    asymmetric_error_y = [err_eff_low_x, err_eff_up_x]
    ax_eff_vs_thr.errorbar(charge, eff_list, yerr=asymmetric_error_y, marker="o",
                           linestyle='-', color=color, markerfacecolor='none', label=label)

    asymmetric_error_x = [err_res_low_mean, err_res_up_mean]
    ax_res_vs_clu.errorbar(clustersize_list, res_list_mean, yerr=asymmetric_error_x,
                           label=label, marker="s", linestyle='', color=color)

    asymmetric_error_x = [err_mean_low_x, err_mean_up_x]
    ax_mean.errorbar(charge, mean_list_x, yerr=asymmetric_error_x,
                     label=label, marker="s", linestyle='', color=color)

    asymmetric_error_y = [err_mean_low_y, err_mean_up_y]
    ax_mean.errorbar(charge, mean_list_y, yerr=asymmetric_error_y,
                     marker="s", linestyle='', color=color, markerfacecolor='none')

    asymmetric_error_y = [err_eff_low_x, err_eff_up_x]
    ax_eff_vs_clu.errorbar(clustersize_list, eff_list, yerr=asymmetric_error_y,
                           marker="s", label=label, linestyle='', color=color, markerfacecolor='none')

x = 0.75
y = 0.95
x3 = 0.35
y3 = 0.30
ax_eff_vs_thr.set_ylabel('Efficiency (%)')    
ax_eff_vs_thr.set_xlabel('Threshold (electrons)')
ax_eff_vs_thr.grid()
ax_eff_vs_thr.set_ylim(69, 101)
ax_eff_vs_thr.set_xlim(70, 400)
ax_eff_vs_thr.text(
    x3, y3,
    STATUS,
    fontsize=12,
    ha='center', va='top',
    transform=ax_eff_vs_thr.transAxes
)

ax_eff_vs_thr.text(
    x3, y3-0.06,
    TEST_BEAM,
    fontsize=9,
    ha='center', va='top',
    transform=ax_eff_vs_thr.transAxes
)

ax_eff_vs_thr.text(1.1, 1.0,
                   CHIP_SETTINGS,
                   fontsize=9,
                   ha='left', va='top',
                   transform=ax_eff_vs_thr.transAxes
                   )
ax_eff_vs_thr.legend(loc='lower right', bbox_to_anchor=(
    1.35, -0.02), prop={"size": 9})


ax_eff_vs_thr.axhline(99, linestyle='dashed', color='grey')
ax_eff_vs_thr.text(ax_eff_vs_thr.get_xlim()[0]-0.014*(ax_eff_vs_thr.get_xlim()[
                   1]-ax_eff_vs_thr.get_xlim()[0]), 99, "99", fontsize=7, ha='right', va='center')
#resution vs cluster size
ax_res_vs_clu.set_ylabel('Resolution (um)')
ax_res_vs_clu.set_xlabel('Average Cluster size (pixel)')
ax_res_vs_clu.legend(loc='lower right', bbox_to_anchor=(
    1.35, -0.02), prop={"size": 9})
ax_res_vs_clu.grid()

ax_res_vs_clu.text(
    x, y,
    STATUS,
    fontsize=12,
    ha='center', va='top',
    transform=ax_res_vs_clu.transAxes
)

ax_res_vs_clu.text(
    x, y-0.06,
    TEST_BEAM,
    fontsize=9,
    ha='center', va='top',
    transform=ax_res_vs_clu.transAxes
)

ax_res_vs_clu.text(1.1, 1.0,
                   CHIP_SETTINGS,
                   fontsize=9,
                   ha='left', va='top',
                   transform=ax_res_vs_clu.transAxes
                   )

#mean vs threshold
ax_mean.set_ylabel('Mean (um)')
ax_mean.set_xlabel('Threshold (electrons)')
ax_mean.legend(loc='lower right', bbox_to_anchor=(
    1.35, -0.02), prop={"size": 9})
ax_mean.set_xlim(70, 400)
ax_mean.grid()
#resolution x vs thr
ax_resx_vs_thr.set_ylabel('Resolution (um)')
ax_cluster_size_x.set_ylabel('Average Cluster size (pixel)')
ax_resx_vs_thr.set_xlabel('Threshold (electrons)')
ax_resx_vs_thr.legend(loc='lower right', bbox_to_anchor=(
    1.35, -0.02), prop={"size": 9})
ax_resx_vs_thr.grid()
ax_resx_vs_thr.legend(loc='lower right', bbox_to_anchor=(
    1.35, -0.02), prop={"size": 9})
ax_resx_vs_thr.set_xlim(70, 400)

#resolution y vs thr
ax_resy_vs_thr.set_ylabel('Resolution (um)')
ax_cluster_size_y.set_ylabel('Average Cluster size (pixel)')
ax_resy_vs_thr.set_xlabel('Threshold (electrons)')
ax_resy_vs_thr.legend(loc='lower right')
ax_resy_vs_thr.grid()

ax_resy_vs_thr.set_xlim(70, 400)

#mean resolution vs thr
ax_resmean_vs_thr.set_ylabel('Resolution (um)')
ax_cluster_size_mean.set_ylabel('Average Cluster size (pixel)')
ax_resmean_vs_thr.set_xlabel('Threshold (electrons)')
ax_resmean_vs_thr.legend(
    loc='lower right', bbox_to_anchor=(1.35, -0.02), prop={"size": 9})
ax_resmean_vs_thr.grid()
ax_resmean_vs_thr.set_xlim(70, 400)
#efficiency vs cluster size
ax_eff_vs_clu.set_ylabel('Efficiency (%)')
ax_eff_vs_clu.set_xlabel('Average Cluster size (pixel)')
ax_eff_vs_clu.grid()
ax_eff_vs_clu.legend(loc='lower right', bbox_to_anchor=(
    1.35, -0.02), prop={"size": 9})


ax_resx_vs_thr.text(
    x, y,
    STATUS,
    fontsize=12,
    ha='center', va='top',
    transform=ax_resx_vs_thr.transAxes
)

ax_resx_vs_thr.text(
    x, y-0.06,
    TEST_BEAM,
    fontsize=9,
    ha='center', va='top',
    transform=ax_resx_vs_thr.transAxes
)

ax_resx_vs_thr.text(1.1, 1.0,
                    CHIP_SETTINGS,
                    fontsize=9,
                    ha='left', va='top',
                    transform=ax_resx_vs_thr.transAxes
                    )


ax_resy_vs_thr.legend(loc='lower right', bbox_to_anchor=(
    1.35, -0.02), prop={"size": 9})

ax_resy_vs_thr.text(
    x, y,
    STATUS,
    fontsize=12,
    ha='center', va='top',
    transform=ax_resy_vs_thr.transAxes
)

ax_resy_vs_thr.text(
    x, y-0.06,
    TEST_BEAM,
    fontsize=9,
    ha='center', va='top',
    transform=ax_resy_vs_thr.transAxes
)

ax_resy_vs_thr.text(1.1, 1.0,
                    CHIP_SETTINGS,
                    fontsize=9,
                    ha='left', va='top',
                    transform=ax_resy_vs_thr.transAxes
                    )

ax_resmean_vs_thr.legend(
    loc='lower right', bbox_to_anchor=(1.35, -0.02), prop={"size": 9})

#ax_resmean_vs_thr.set_ylim(1, 7.25)
ax_resmean_vs_thr.text(
    x, y,
    STATUS,
    fontsize=12,
    ha='center', va='top',
    transform=ax_resmean_vs_thr.transAxes
)

ax_resmean_vs_thr.text(
    x, y-0.06,
    TEST_BEAM,
    fontsize=9,
    ha='center', va='top',
    transform=ax_resmean_vs_thr.transAxes
)

ax_resmean_vs_thr.text(1.1, 1.0,
                       CHIP_SETTINGS,
                       fontsize=9,
                       ha='left', va='top',
                       transform=ax_resmean_vs_thr.transAxes
                       )

ax_mean.text(
    x, y,
    STATUS,
    fontsize=12,
    ha='center', va='top',
    transform=ax_mean.transAxes
)

ax_mean.text(
    x, y-0.06,
    TEST_BEAM,
    fontsize=9,
    ha='center', va='top',
    transform=ax_mean.transAxes
)

ax_mean.text(1.1, 1.0,
             CHIP_SETTINGS,
             fontsize=9,
             ha='left', va='top',
             transform=ax_mean.transAxes
             )

ax_eff_vs_clu.text(
    x, y,
    STATUS,
    fontsize=12,
    ha='center', va='top',
    transform=ax_eff_vs_clu.transAxes
)

ax_eff_vs_clu.text(
    x, y-0.06,
    TEST_BEAM,
    fontsize=9,
    ha='center', va='top',
    transform=ax_eff_vs_clu.transAxes
)

ax_eff_vs_clu.text(1.1, 1.0,
                   CHIP_SETTINGS,
                   fontsize=9,
                   ha='left', va='top',
                   transform=ax_eff_vs_clu.transAxes
                   )

fig_eff_vs_thr.savefig(plots_dir+'/efficiencyVsThreshold_' +
                       FILE_SUFFIX+'_'+fit_label+'.png', dpi=600)
fig_eff_vs_clu.savefig(plots_dir+'/efficiencyVsClustersize_list_' +
                       FILE_SUFFIX+'_'+fit_label+'.png', dpi=600)
fig_mean.savefig(plots_dir+'/meanVsThr_' +
                 FILE_SUFFIX+'_'+fit_label+'.png', dpi=600)
fig_res_vs_clu.savefig(plots_dir+'/resVsClustersize_list_' +
                       FILE_SUFFIX+'_'+fit_label+'.png', dpi=600)
fig_resx_vs_thr.savefig(plots_dir+'/resolutionVsThreshold_x_' +
                        FILE_SUFFIX+'_'+fit_label+'.png', dpi=600)
fig_resy_vs_thr.savefig(plots_dir+'/resolutionVsThreshold_y_' +
                        FILE_SUFFIX+'_'+fit_label+'.png', dpi=600)
fig_resmean_vs_thr.savefig(
    plots_dir+'/resolutionVsThreshold_mean_'+FILE_SUFFIX+'_'+fit_label+'.png', dpi=600)

fit_info.Close()
