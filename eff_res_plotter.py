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
parser.add_argument('-r', '--plotfhr',
                    help='Plot the fake hit rate', action='store_true')
parser.add_argument('-gl', '--gaussianlimit',
                    help='Use gaussian fit for the noise limit', action='store_true')
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
plotfhr = args.plotfhr
use_gaussianlimit = args.gaussianlimit

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
FHR_PATHS = params['FHR_PATHS']
NSIGMANOISE = params['NSIGMANOISE']
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

# tracking resolution from telescope-optimizer
tracking_resolution_x_SPS = 2.08
tracking_resolution_y_SPS = 2.08
tracking_resolution_x_PSJune = 2.84
tracking_resolution_y_PSJune = 2.84
tracking_resolution_x_PSAugust = 2.43
tracking_resolution_y_PSAugust = 2.43


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
if plotfhr:
    ax_fhr_vs_thr = ax_eff_vs_thr.twinx()
    ax_eff_vs_thr.errorbar([], [], ([], []), label="Fake hit probability", marker='s',
                        markerfacecolor='none', linestyle='dashed', elinewidth=1.3, capsize=1.5, color='dimgrey')


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
if use_fit:
    fit_info = TFile(plots_dir+"/fit_info.root", "recreate")

for file_path_list, fhr_path, label, chip, color in zip(FILE_PATHS, FHR_PATHS, LABELS, CHIPS, COLORS):
    if use_fit or use_gaussianlimit:
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
    err_fhr_up_x = []
    err_fhr_low_x = []
    fhr_list = []
    
    fhr_file = TFile(fhr_path, "read")
    
    if chip == "AF25P_W22_1.2V" or "June" in label:
        apts = "4"
    else:
        apts = "3"

    pixel_values = fhr_file.Get(
        "EventLoaderEUDAQ2/APTS_"+apts+"/hPixelRawValues")
    if use_gaussianlimit:
        noise_function = TF1("noise", "gaus(0)",-40,40)
        pixel_values.Fit(noise_function,'MRQ+')
        eThrLimit = (noise_function.GetParameter(2)*NSIGMANOISE+noise_function.GetParameter(1))*100/hundredElectronToADCu[chip]
        sub_dir.cd()
        noise_function.Write()
    else:
        eThrLimit = (pixel_values.GetStdDev()*NSIGMANOISE+pixel_values.GetMean())*100/hundredElectronToADCu[chip]
    fhr_file.Close()

    print("plotting above ",eThrLimit," electrons")
    for file_path in file_path_list:
        print(file_path)
        thr = int(re.findall(r'\d+', file_path)[-1])
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
        if plotfhr:
            # compute the fake hits
            n_events = pixel_values.GetEntries()
            bin_min = pixel_values.GetXaxis().FindBin(thr)
            fake_hits = pixel_values.Integral(bin_min, pixel_values.GetNbinsX()+1)
            fhr_list.append(fake_hits/n_events)
            err_fhr_up_x.append(math.sqrt(fake_hits)/n_events)
            err_fhr_low_x.append(math.sqrt(fake_hits)/n_events)
        
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
            print(file_path)
            res_x = math.sqrt(residualsX.GetStdDev() **
                              2-tracking_resolution_x**2)
            res_y = math.sqrt(residualsY.GetStdDev() **
                              2-tracking_resolution_y**2)
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
    if plotfhr:
        asymmetric_error_y = [err_fhr_low_x, err_fhr_up_x]
        ax_fhr_vs_thr.errorbar(charge, fhr_list, yerr=asymmetric_error_y,
                            marker="s", linestyle='-', color=color, markerfacecolor='none')

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
if plotfhr:
    ax_fhr_vs_thr.set_ylabel('P(pixel above threshold)')
    ax_fhr_vs_thr.set_ylim(-0.01/32., 0.01+0.01/32.)
ax_eff_vs_thr.set_xlabel('Threshold (electrons)')
ax_eff_vs_thr.grid()
ax_eff_vs_thr.set_ylim(69, 101)
ax_eff_vs_thr.set_xlim(eThrLimit, 400)
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
ax_eff_vs_thr.text(ax_resx_vs_thr.get_xlim()[0]-0.014*(ax_resx_vs_thr.get_xlim()[
                   1]-ax_resx_vs_thr.get_xlim()[0]), 99, "99", fontsize=7, ha='right', va='center')
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
ax_mean.set_xlim(eThrLimit, 400)
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
ax_resx_vs_thr.set_xlim(eThrLimit, 400)

#resolution y vs thr
ax_resy_vs_thr.set_ylabel('Resolution (um)')
ax_cluster_size_y.set_ylabel('Average Cluster size (pixel)')
ax_resy_vs_thr.set_xlabel('Threshold (electrons)')
ax_resy_vs_thr.legend(loc='lower right')
ax_resy_vs_thr.grid()

ax_resy_vs_thr.set_xlim(eThrLimit, 400)

#mean resolution vs thr
ax_resmean_vs_thr.set_ylabel('Resolution (um)')
ax_cluster_size_mean.set_ylabel('Average Cluster size (pixel)')
ax_resmean_vs_thr.set_xlabel('Threshold (electrons)')
ax_resmean_vs_thr.legend(
    loc='lower right', bbox_to_anchor=(1.35, -0.02), prop={"size": 9})
ax_resmean_vs_thr.grid()
ax_resmean_vs_thr.set_xlim(eThrLimit, 400)
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

ax_resmean_vs_thr.set_ylim(1, 4.25)
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
