from ROOT import TFile, TF1, TMath
import matplotlib as mpl
import matplotlib.pyplot as plt
import math
import argparse
import yaml
import os
import re
from utils import utils
from datetime import date, datetime
import numpy as np

association_window = "75"
plot_date = str(date.today().day) + ' ' + datetime.now().strftime("%b") + ' ' + str(date.today().year)


from matplotlib import rcParams
from cycler import cycler
import matplotlib.style as style
style.use('wp3.mplstyle')
colors = {
    "sky blue":       "#56B4E9",
    "orange":         "#E69F00",
    "bluish green":   "#009E73",
    "reddish purple": "#CC79A7",
    "blue":           "#0072B2",
    "vermillion":     "#D55E00",
    "yellow":         "#F0E442"
}

rcParams['axes.prop_cycle'] = cycler('color', colors.values())


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
parser.add_argument('-m', '--mostcentral',
                    help='Keep n% most central counts', type=float, default=100)
parser.add_argument('-c', '--csize',
                    help='Get residuals of the cluster with the selected cluster size', type=int, default=0)
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
most_central = args.mostcentral
cluster_size = args.csize

res_file_suffix = ""
if most_central<100:
    res_file_suffix += "_top"+str(most_central)
if use_fit:
    if use_qGaussian:
        res_file_suffix += "_qgauss"
    elif use_exp_gaussian:
        res_file_suffix += "_expgauss"
    else:
        res_file_suffix += "_gauss"

if cluster_size > 4:
    print("ERROR: max cluster size must be below 4 -> setting it to 0")
    cluster_size = 0

if use_qGaussian and use_exp_gaussian:
    print("ATTENTION: both qGaussian and gaussian with exp-tails are selected")
    use_exp_gaussian = False
if use_fit:
    fit_label = "fit"
else:
    fit_label = "rms"

use_geometric = args.geometric

FILE_SUFFIX = params['FILE_SUFFIX']
CHIPS = params['CHIPS']
LABELS = params['LABELS']
FILE_PATHS = params['FILE_PATHS']
STATUS = '$\\bf{ITS3}$ beam test '+params['STATUS']
TEST_BEAM = ''
for TEST in params['TEST_BEAMS']:
    TEST_BEAM += TEST + "\n"
NOISE_PATHS = params['NOISE_PATHS']
NSIGMANOISE = params['NSIGMANOISE']
if NSIGMANOISE == 0:
    NOISE_PATHS = [None] * len(FILE_PATHS)
TRACKINGRESOLUTIONS = params['TRACKINGRESOLUTIONS']

CHIP_SETTINGS =  params['CHIP_SETTINGS'] #'\n'.join(params['CHIP_SETTINGS'])

EFF_RANGE = params['EFF_RANGE']
THR_RANGE = params['THR_RANGE']
RES_RANGE = params['RES_RANGE']
CLU_RANGE = params['CLU_RANGE']

TEXT_RES = params['TEXT_RES']
TEXT_EFF = params['TEXT_EFF']
SETTING_RES = params['SETTING_RES']
SETTING_EFF = params['SETTING_EFF']
LEGEND_RES = params['LEGEND_RES']
LEGEND_EFF = params['LEGEND_EFF']
NTICKS = params['NTICKS']
plots_dir = "plots/"+FILE_SUFFIX
if not os.path.isdir(plots_dir):
    os.mkdir(plots_dir)

# plot of the resolution (Average cluster size) vs thr
fig_resx_vs_thr, ax_resx_vs_thr = plt.subplots(figsize=(11, 5))
plt.subplots_adjust(left=0.07, right=0.75, top=0.95)

ax_cluster_size_x = ax_resx_vs_thr.twinx()

ax_resx_vs_thr.errorbar([], [], ([], []), label="x-position resolution ",
                        marker='s', elinewidth=1.3, capsize=1.5, color='dimgrey')
ax_resx_vs_thr.errorbar([], [], ([], []), label="Average cluster size", marker='s',
                        markerfacecolor='none', linestyle='dashed', elinewidth=1.3, capsize=1.5, color='dimgrey')

fig_resy_vs_thr, ax_resy_vs_thr = plt.subplots(figsize=(11, 5))
plt.subplots_adjust(left=0.07, right=0.75, top=0.95)

ax_cluster_size_y = ax_resy_vs_thr.twinx()

ax_resy_vs_thr.errorbar([], [], ([], []), label="y-position resolution",
                        marker='s', linestyle='dashed', elinewidth=1.3, capsize=1.5, color='dimgrey')
ax_resy_vs_thr.errorbar([], [], ([], []), label="Average cluster size", marker='s',
                        markerfacecolor='none', linestyle='dashed', elinewidth=1.3, capsize=1.5, color='dimgrey')

fig_resmean_vs_thr, ax_resmean_vs_thr = plt.subplots(figsize=(11, 5))
plt.subplots_adjust(left=0.07, right=0.75, top=0.95)

ax_cluster_size_mean = ax_resmean_vs_thr.twinx()

ax_resmean_vs_thr.errorbar([], [], ([], []), label="Spatial resolution",
                           marker='s', elinewidth=1.3, capsize=1.5, color='dimgrey')
ax_resmean_vs_thr.errorbar([], [], ([], []), label="Average cluster size", marker='s',
                           markerfacecolor='none', linestyle='dashed', elinewidth=1.3, capsize=1.5, color='dimgrey')

# plot of the efficiency vs thr
fig_eff_vs_thr, ax_eff_vs_thr = plt.subplots(figsize=(11, 5))
plt.subplots_adjust(left=0.07, right=0.75, top=0.95)
ax_eff_vs_thr.errorbar([], [], ([], []), label="Detection efficiency", marker='s',
                       linestyle='-', elinewidth=1.3, capsize=1.5, color='dimgrey')


# plot of the resolution vs Average cluster size
fig_res_vs_clu, ax_res_vs_clu = plt.subplots(figsize=(11, 5))
plt.subplots_adjust(left=0.07, right=0.75, top=0.95)
ax_res_vs_clu.errorbar([], [], ([], []), label="resolution",
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
fit_info = TFile(plots_dir+"/fit_info"+res_file_suffix+".root", "recreate")

binary_resolutions = []
for file_path_list, noise_path, label, chip, track_res in zip(FILE_PATHS, NOISE_PATHS, LABELS, CHIPS, TRACKINGRESOLUTIONS):
    
    bin_res = float(re.findall(r'\d+', chip)[0])/math.sqrt(12)
    if bin_res not in binary_resolutions:
        binary_resolutions.append(bin_res)
    
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

    #get apts Id
    root_file = TFile(file_path_list[0], "READ")
    subdir = root_file.Get("AnalysisDUT")
    key_list = subdir.GetListOfKeys()
    dir_list = []
    for key in key_list:
        if key.GetClassName() == "TDirectoryFile":
            dir_list.append(key.GetName())
    apts = dir_list[0]
    root_file.Close()

    eThrLimit = 0
    if use_limit and NSIGMANOISE > 0:
        noise_file = TFile(noise_path, "read")
        noise_values = noise_file.Get(
            "EventLoaderEUDAQ2/"+apts+"/hPixelRawValues")
        eThrLimit = (noise_values.GetStdDev()*NSIGMANOISE) * \
            100/utils.hundredElectronToADCu[chip]
        print("plotting above ", eThrLimit, " $\it{e}^{-}$")
        noise_file.Close()

    for file_path in file_path_list:
        print(file_path)
        thr = int(re.findall(r'\d+', file_path)[-1])
        if thr*100/utils.hundredElectronToADCu[chip] < eThrLimit:
            continue
        input_file = TFile(file_path, "read")

        size_label = ""
        if cluster_size > 0:
            size_label = str(cluster_size)+"pix"
        residualsX = input_file.Get(
            "AnalysisDUT/"+apts+"/local_residuals/residualsX"+size_label)
        residualsY = input_file.Get(
            "AnalysisDUT/"+apts+"/local_residuals/residualsY"+size_label)
        clusterSize = input_file.Get(
            "AnalysisDUT/"+apts+"/clusterSizeAssociated")
        efficiency = input_file.Get(
            "AnalysisEfficiency/"+apts+"/eTotalEfficiency")

        eff_list.append(100*efficiency.GetEfficiency(1))
        err_eff_up_x.append(100*efficiency.GetEfficiencyErrorUp(1))
        err_eff_low_x.append(100*efficiency.GetEfficiencyErrorLow(1))
        charge.append(100*thr/utils.hundredElectronToADCu[chip])

        utils.clean_residuals(residualsX, most_central)
        utils.clean_residuals(residualsY, most_central)
        residualsX.Rebin(4)
        residualsY.Rebin(4)


        if use_fit:
            mean_par = 4
            sigma_par = 1
            if use_qGaussian:
                func = TF1("qGauss", utils.qGauss, -40, 40, 5)
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
                func = TF1("qGauss", utils.gauss_exp_tails, -40, 40, 5)
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

            residualsX.Fit(func, "QMR+")

            res_x = math.sqrt(func.GetParameter(sigma_par)
                              ** 2-track_res[0]**2)

            err_res_x = func.GetParError(sigma_par)
            mean_x = func.GetParameter(mean_par)
            err_mean_x = func.GetParError(mean_par)
            residualsY.Fit(func, "QMR+")
            res_y = math.sqrt(func.GetParameter(sigma_par)
                              ** 2-track_res[1]**2)
            err_res_y = func.GetParError(sigma_par)
            mean_y = func.GetParameter(mean_par)
            err_mean_y = func.GetParError(mean_par)

        else:
            if residualsX.GetStdDev() ** 2-track_res[0]**2 > 0:
                res_x = math.sqrt(residualsX.GetStdDev() **
                                  2-track_res[0]**2)
                res_y = math.sqrt(residualsY.GetStdDev() **
                                  2-track_res[1]**2)
            else:
                res_x = 0
                res_y = 0
            err_res_x = residualsX.GetStdDevError()
            err_res_y = residualsY.GetStdDevError()
            mean_x = residualsX.GetMean()
            mean_y = residualsY.GetMean()
            err_mean_x = residualsX.GetMeanError()
            err_mean_y = residualsY.GetMeanError()

        sub_dir.cd()
        residualsX.SetName('residualsX_'+chip+'_thr_'+str(thr))
        residualsY.SetName('residualsY_'+chip+'_thr_'+str(thr))
        residualsX.Write()
        residualsY.Write()
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
    
    print("efficiency: ", eff_list)
    print("resolution: ", res_list_mean)
    print("charge: ", charge)

    color = None
    if chip == "AF15P_W22_1.2V":
        color = 'black'

    asymmetric_error_x = [err_res_low_x, err_res_up_x]
    ax_resx_vs_thr.errorbar(charge, res_list_x, yerr=asymmetric_error_x,
                            label=label, marker="s", linestyle='', color = color)

    asymmetric_error_y = [err_res_low_y, err_res_up_y]
    ax_resy_vs_thr.errorbar(charge, res_list_y, yerr=asymmetric_error_y,
                            label=label, marker="s", linestyle='', color = color)

    asymmetric_error_y = [err_res_low_mean, err_res_up_mean]
    ax_resmean_vs_thr.errorbar(charge, res_list_mean, yerr=asymmetric_error_y,
                               label=label, marker="s", linestyle='-', color = color)

    asymmetric_error_y = [err_clustersize_list, err_clustersize_list]
    ax_cluster_size_x.errorbar(charge, clustersize_list, yerr=asymmetric_error_y,
                               marker="s", linestyle='', markerfacecolor='none', color = color)

    asymmetric_error_y = [err_clustersize_list, err_clustersize_list]
    ax_cluster_size_y.errorbar(charge, clustersize_list, yerr=asymmetric_error_y,
                               marker="s", linestyle='', markerfacecolor='none', color = color)

    asymmetric_error_y = [err_clustersize_list, err_clustersize_list]
    ax_cluster_size_mean.errorbar(charge, clustersize_list, yerr=asymmetric_error_y,
                                  marker="s", linestyle='--', markerfacecolor='none', color = color)

    asymmetric_error_y = [err_eff_low_x, err_eff_up_x]
    ax_eff_vs_thr.errorbar(charge, eff_list, yerr=asymmetric_error_y, marker="s",
                           linestyle='-', label=label, color = color)

    asymmetric_error_x = [err_res_low_mean, err_res_up_mean]
    ax_res_vs_clu.errorbar(clustersize_list, res_list_mean, yerr=asymmetric_error_x,
                           label=label, marker="s", linestyle='', color = color)

    asymmetric_error_x = [err_mean_low_x, err_mean_up_x]
    ax_mean.errorbar(charge, mean_list_x, yerr=asymmetric_error_x,
                     label=label, marker="s", linestyle='', color = color)

    asymmetric_error_y = [err_mean_low_y, err_mean_up_y]
    ax_mean.errorbar(charge, mean_list_y, yerr=asymmetric_error_y,
                     marker="s", linestyle='', markerfacecolor='none', color = color)

    asymmetric_error_y = [err_eff_low_x, err_eff_up_x]
    ax_eff_vs_clu.errorbar(clustersize_list, eff_list, yerr=asymmetric_error_y,
                           marker="s", label=label, linestyle='', markerfacecolor='none', color = color)


x = 0.75
y = 0.98
x3 = 0.35
y3 = 0.30
ax_eff_vs_thr.set_ylabel('Detection efficiency (%)')
ax_eff_vs_thr.set_xlabel('Threshold ($\it{e}^{-}$)')
ax_eff_vs_thr.grid()

if THR_RANGE is not None:
    ax_eff_vs_thr.set_xlim(THR_RANGE[0], THR_RANGE[1])
if EFF_RANGE is not None:
    ax_eff_vs_thr.set_ylim(EFF_RANGE[0], EFF_RANGE[1])

ax_eff_vs_thr.text(
    TEXT_EFF[0], TEXT_EFF[1],
    STATUS,
    fontsize=12,
    ha='left', va='top',
    transform=ax_eff_vs_thr.transAxes
)

ax_eff_vs_thr.text(
    TEXT_EFF[0], TEXT_EFF[1]-0.06,
    TEST_BEAM+'Plotted on {}'.format(plot_date),
    fontsize=9,
    ha='left', va='top',
    transform=ax_eff_vs_thr.transAxes
)

ax_eff_vs_thr.text(0.02,0.015,
    "Association window radius: %s \u03BCm"%association_window + ", no pixel masking. Plotting for thresholds above "+str(NSIGMANOISE)+"$\\times$noise RMS.",
    fontsize=10,
    ha='left', va='center',
    transform=ax_eff_vs_thr.transAxes
)


ax_eff_vs_thr.text(SETTING_EFF[0],SETTING_EFF[1],
                   CHIP_SETTINGS,
                   fontsize=9,
                   ha='left', va='top',
                   transform=ax_eff_vs_thr.transAxes
                   )
ax_eff_vs_thr.legend(loc='lower right', bbox_to_anchor=(
    LEGEND_EFF[0], LEGEND_EFF[1]), prop={"size": 9})


ax_eff_vs_thr.axhline(99, linestyle='dashed', color='grey')
ax_eff_vs_thr.text(ax_eff_vs_thr.get_xlim()[0]-0.014*(ax_eff_vs_thr.get_xlim()[
                   1]-ax_eff_vs_thr.get_xlim()[0]), 99, "99", fontsize=8, ha='right', va='center')

# resution vs cluster size
ax_res_vs_clu.set_ylabel('Spatial resolution (\u03BCm)')
ax_res_vs_clu.set_xlabel('Average Cluster size (pixel)')
ax_res_vs_clu.legend(loc='lower right', bbox_to_anchor=(
    1.35, 0), prop={"size": 9})
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
    ha='left', va='top',
    transform=ax_res_vs_clu.transAxes
)

ax_res_vs_clu.text(1.12, 1.0,
                   CHIP_SETTINGS,
                   fontsize=9,
                   ha='left', va='top',
                   transform=ax_res_vs_clu.transAxes
                   )

# mean vs threshold
ax_mean.set_ylabel('Mean (um)')
ax_mean.set_xlabel('Threshold ($\it{e}^{-}$)')
ax_mean.legend(loc='lower right', bbox_to_anchor=(
    1.35, 0), prop={"size": 9})
ax_mean.set_xlim(THR_RANGE[0], THR_RANGE[1])
ax_mean.grid()

# resolution x vs thr
ax_resx_vs_thr.set_ylabel('Spatial resolution (\u03BCm)')
ax_cluster_size_x.set_ylabel('Average Cluster size (pixel)')
ax_resx_vs_thr.set_xlabel('Threshold ($\it{e}^{-}$)')
ax_resx_vs_thr.legend(loc='lower right', bbox_to_anchor=(
    1.35, 0), prop={"size": 9})
ax_resx_vs_thr.grid()
ax_resx_vs_thr.legend(loc='lower right', bbox_to_anchor=(
    1.35, 0), prop={"size": 9})
if THR_RANGE is not None:
    ax_resx_vs_thr.set_xlim(THR_RANGE[0], THR_RANGE[1])
if RES_RANGE is not None:
    ax_resx_vs_thr.set_ylim(RES_RANGE[0], RES_RANGE[1])
if CLU_RANGE is not None:
    ax_cluster_size_x.set_ylim(CLU_RANGE[0], CLU_RANGE[1])

# resolution y vs thr
ax_resy_vs_thr.set_ylabel('Spatial resolution (\u03BCm)')
ax_cluster_size_y.set_ylabel('Average Cluster size (pixel)')
ax_resy_vs_thr.set_xlabel('Threshold ($\it{e}^{-}$)')
ax_resy_vs_thr.legend(loc='lower right')
ax_resy_vs_thr.grid()
if THR_RANGE is not None:
    ax_resy_vs_thr.set_xlim(THR_RANGE[0], THR_RANGE[1])
if RES_RANGE is not None:
    ax_resy_vs_thr.set_ylim(RES_RANGE[0], RES_RANGE[1])
if CLU_RANGE is not None:
    ax_cluster_size_y.set_ylim(CLU_RANGE[0], CLU_RANGE[1])

# mean resolution vs thr
ax_resmean_vs_thr.set_ylabel('Spatial resolution (\u03BCm)')
ax_cluster_size_mean.set_ylabel('Average Cluster size (pixel)')
ax_resmean_vs_thr.set_xlabel('Threshold ($\it{e}^{-}$)')
ax_resmean_vs_thr.legend(
    loc='lower right', bbox_to_anchor=(LEGEND_RES[0], LEGEND_RES[1]), prop={"size": 9})
ax_resmean_vs_thr.grid()
if THR_RANGE is not None:
    ax_resmean_vs_thr.set_xlim(THR_RANGE[0], THR_RANGE[1])
if RES_RANGE is not None:
    ax_resmean_vs_thr.set_ylim(RES_RANGE[0], RES_RANGE[1])
if CLU_RANGE is not None:
    ax_cluster_size_mean.set_ylim(CLU_RANGE[0], CLU_RANGE[1])
# efficiency vs cluster size
from matplotlib.ticker import FuncFormatter

ax_cluster_size_mean.yaxis.set_major_formatter(FuncFormatter(lambda y, _: '{:.2f}'.format(y)))

ax_resmean_vs_thr.set_yticks(np.linspace(ax_resmean_vs_thr.get_ybound()[0], ax_resmean_vs_thr.get_ybound()[1], NTICKS))
ax_cluster_size_mean.set_yticks(np.linspace(ax_cluster_size_mean.get_ybound()[0], ax_cluster_size_mean.get_ybound()[1], NTICKS))
ax_eff_vs_clu.set_ylabel('Detection efficiency (%)')
ax_eff_vs_clu.set_xlabel('Average Cluster size (pixel)')
ax_eff_vs_clu.grid()
ax_eff_vs_clu.legend(loc='lower right', bbox_to_anchor=(
    1.35, 0), prop={"size": 9})


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
    1.35, 0), prop={"size": 9})

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

for res in binary_resolutions:
    ax_resmean_vs_thr.axhline(res,linestyle='dashed',color='grey')
    binary_label = "Pitch/$\\sqrt{12}$"
    if len(binary_resolutions) >1:
        binary_label = "%s \u03BCm/$\\sqrt{12}$"% int(round(res*math.sqrt(12),0))
        ax_resmean_vs_thr.text(ax_resmean_vs_thr.get_xlim()[1]-0.05, res+0.15,
            binary_label, fontsize=10,
            ha='right', va='center',color='grey'
        )
    else:
        ax_resmean_vs_thr.text(ax_resmean_vs_thr.get_xlim()[0]+0.165*(ax_resmean_vs_thr.get_xlim()[1]-ax_resmean_vs_thr.get_xlim()[0]), res-0.15,
            binary_label, fontsize=10,
            ha='right', va='center',color='grey'
        )

ax_resmean_vs_thr.text(
    TEXT_RES[0], TEXT_RES[1],
    STATUS,
    fontsize=12,
    ha='left', va='top',
    transform=ax_resmean_vs_thr.transAxes
)

ax_resmean_vs_thr.text(
    TEXT_RES[0], TEXT_RES[1]-0.06,
    TEST_BEAM+ 'Plotted on {}'.format(plot_date),
    fontsize=9,
    ha='left', va='top',
    transform=ax_resmean_vs_thr.transAxes
)

ax_resmean_vs_thr.text(0.02,0.015,
    "Association window radius: %s \u03BCm"%association_window + ", no pixel masking. Plotting for thresholds above "+str(NSIGMANOISE)+"$\\times$noise RMS.",
    fontsize=10,
    ha='left', va='center',
    transform=ax_resmean_vs_thr.transAxes
)
ax_resmean_vs_thr.text(SETTING_RES[0],SETTING_RES[1],
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

ax_eff_vs_clu.text(1.12, 1.0,
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
