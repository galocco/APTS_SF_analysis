from ROOT import TFile
import matplotlib.pyplot as plt
import math
import argparse
import yaml
import os
import re
import utils
from datetime import date, datetime
import numpy as np
import json
from matplotlib.ticker import FuncFormatter
  

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
markers={
    "square":         "s",
    "triangle_down":  "v",
    "circle":         "o",
    "diamond":        "D",
    "hexagon1":       "h",
    "pentagon":       "p",
    "plus":           "P"
}

rcParams['axes.prop_cycle'] = cycler('color', colors.values()) + cycler('marker', markers.values())

parser = argparse.ArgumentParser()
parser.add_argument("config", help="Path to the YAML configuration file")
args = parser.parse_args()

with open(os.path.expandvars(args.config), 'r') as stream:
    try:
        params = yaml.full_load(stream)
    except yaml.YAMLError as exc:
        print(exc)

FILE_SUFFIX = params['FILE_SUFFIX']
CHIPS = params['CHIPS']
LABELS = params['LABELS']
STATUS = '$\\bf{ALICE\ ITS3}$ beam test '+params['STATUS']
TEST_BEAM = params['TEST_BEAMS']
NOISE_PATHS = params['NOISE_PATHS']
NSIGMANOISE = params['NSIGMANOISE']
TRACKINGRESOLUTIONS = params['TRACKINGRESOLUTIONS']

DATA = []
for chip in CHIPS:
    f = open("data/"+chip+".json")
    chip_data = json.load(f)
    DATA.append(chip_data)

CHIP_SETTINGS =  params['CHIP_SETTINGS']

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
if "binary" in CHIPS[0]:
    resolution = "Digital spatial"
else:
    resolution = "Spatial"

fig_resmean_vs_thr, ax_resmean_vs_thr = plt.subplots(figsize=(13, 6))
plt.subplots_adjust(left=0.07, right=0.65, top=0.95)

ax_cluster_size_mean = ax_resmean_vs_thr.twinx()

ax_resmean_vs_thr.errorbar([], [], ([], []), label=resolution+" resolution",
                           marker='s', elinewidth=1.3, capsize=1.5, color='dimgrey')
ax_resmean_vs_thr.errorbar([], [], ([], []), label="Average cluster size", marker='s',
                           markerfacecolor='none', linestyle='dashed', elinewidth=1.3, capsize=1.5, color='dimgrey')

# plot of the efficiency vs thr
fig_eff_vs_thr, ax_eff_vs_thr = plt.subplots(figsize=(13, 6))
plt.subplots_adjust(left=0.07, right=0.65, top=0.95)
ax_eff_vs_thr.errorbar([], [], ([], []), marker='s',
                       linestyle='-', elinewidth=1.3, capsize=1.5, color='dimgrey')
hasPS = False
for label, data, chip, track_res in zip(LABELS, DATA, CHIPS, TRACKINGRESOLUTIONS):
    color = None
    marker = None
    
    if "AF15P_W22_1.2V" in data["chip"]:
        color = 'black'
    if "AF15B_W22_1.2V" in data["chip"]:
        color = 'black'
    if "AF20P_W22_1.2V" in data["chip"]:
        hasPS = True

    charge = [ x * 100/utils.hundredElectronToADCu[data["chip"]] for x in data["threshold"] ]

    data["residuals_x_rms"] = [math.sqrt(x**2-track_res[0]**2) for x in data["residuals_x_rms"]]
    data["residuals_y_rms"] = [math.sqrt(x**2-track_res[1]**2) for x in data["residuals_y_rms"]]

    res_list_mean = [ (x+y)/2. for x,y in zip(data["residuals_x_rms"],data["residuals_y_rms"]) ]

    asymmetric_error_y = [data["err_residuals"], data["err_residuals"]]
    ax_resmean_vs_thr.errorbar(charge, res_list_mean, yerr=asymmetric_error_y,
                               label=label, marker = marker, linestyle='-', color = color)
    asymmetric_error_y = [data["err_clustersize"], data["err_clustersize"]]
    ax_cluster_size_mean.errorbar(charge, data["clustersize"], yerr=asymmetric_error_y,
                                  marker=marker, linestyle='--', markerfacecolor='none', color = color)

    asymmetric_error_y = [data["err_eff_low"], data["err_eff_up"]]
    ax_eff_vs_thr.errorbar(charge, data["efficiency"], yerr=asymmetric_error_y, marker=marker,
                           linestyle='-', label=label, color = color)
    print(data["chip"])
    print("efficiency: ", data["efficiency"])
    print("resolution: ", res_list_mean)
    print("charge: ", charge)

    if "AF15B_W22_1.2V" in data["chip"]:
        ax_resmean_vs_thr.errorbar([], [], marker = "H", linestyle='-', color = None)
        ax_cluster_size_mean.errorbar([], [], marker="H", linestyle='--', color = None)
        ax_eff_vs_thr.errorbar([], [], marker=marker, linestyle='-', color = None)


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
    fontsize=15,
    ha='left', va='top',
    transform=ax_eff_vs_thr.transAxes
)

ax_eff_vs_thr.text(
    TEXT_EFF[0], TEXT_EFF[1]-0.04,
    TEST_BEAM[0],
    fontsize=14,
    ha='left', va='top',
    transform=ax_eff_vs_thr.transAxes
)
if hasPS:
    ax_eff_vs_thr.text(
        TEXT_EFF[0], TEXT_EFF[1]-0.08,
        TEST_BEAM[1],
        fontsize=14,
        ha='left', va='top',
        transform=ax_eff_vs_thr.transAxes
    )

if hasPS:
    posy = 0.12
else:
    posy = 0.08
ax_eff_vs_thr.text(
    TEXT_EFF[0], TEXT_EFF[1]-posy,
    ""+'Plotted on {}'.format(plot_date),
    fontsize=14,
    ha='left', va='top',
    transform=ax_eff_vs_thr.transAxes
)

ax_eff_vs_thr.text(0.02,0.015,
    "Association window radius: %s \u03BCm"%association_window + ". Plotting for thresholds above "+str(NSIGMANOISE)+"$\\times$noise RMS.",
    fontsize=10,
    ha='left', va='center',
    transform=ax_eff_vs_thr.transAxes
)


ax_eff_vs_thr.text(SETTING_EFF[0],SETTING_EFF[1],
                   CHIP_SETTINGS,
                   fontsize=12,
                   ha='left', va='top',
                   transform=ax_eff_vs_thr.transAxes
                   )
ax_eff_vs_thr.legend(loc='lower right', bbox_to_anchor=(
    LEGEND_EFF[0], LEGEND_EFF[1]), prop={"size": 14})


ax_eff_vs_thr.axhline(99, linestyle='dashed', color='grey')
ax_eff_vs_thr.text(ax_eff_vs_thr.get_xlim()[0]-0.014*(ax_eff_vs_thr.get_xlim()[
                   1]-ax_eff_vs_thr.get_xlim()[0]), 99, "99", fontsize=8, ha='right', va='center')

ax_resmean_vs_thr.set_ylabel(resolution+' resolution (\u03BCm)')
ax_cluster_size_mean.set_ylabel('Average cluster size (pixel)')
ax_resmean_vs_thr.set_xlabel('Threshold ($\it{e}^{-}$)')
ax_resmean_vs_thr.legend(
    loc='lower right', bbox_to_anchor=(LEGEND_RES[0], LEGEND_RES[1]), prop={"size": 14})

ax_resmean_vs_thr.grid()


if THR_RANGE is not None:
    ax_resmean_vs_thr.set_xlim(THR_RANGE[0], THR_RANGE[1])
if RES_RANGE is not None:
    ax_resmean_vs_thr.set_ylim(RES_RANGE[0], RES_RANGE[1])
if CLU_RANGE is not None:
    ax_cluster_size_mean.set_ylim(CLU_RANGE[0], CLU_RANGE[1])

ax_cluster_size_mean.yaxis.set_major_formatter(FuncFormatter(lambda y, _: '{:.2f}'.format(y)))

ax_resmean_vs_thr.set_yticks(np.linspace(ax_resmean_vs_thr.get_ybound()[0], ax_resmean_vs_thr.get_ybound()[1], NTICKS))
ax_cluster_size_mean.set_yticks(np.linspace(ax_cluster_size_mean.get_ybound()[0], ax_cluster_size_mean.get_ybound()[1], NTICKS))


ax_resmean_vs_thr.text(
    TEXT_RES[0], TEXT_RES[1],
    STATUS,
    fontsize=15,
    ha='left', va='top',
    transform=ax_resmean_vs_thr.transAxes
)

ax_resmean_vs_thr.text(
    TEXT_RES[0], TEXT_RES[1]-0.04,
    TEST_BEAM[0],
    fontsize=14,
    ha='left', va='top',
    transform=ax_resmean_vs_thr.transAxes
)

if hasPS:
    ax_resmean_vs_thr.text(
        TEXT_RES[0], TEXT_RES[1]-0.08,
        TEST_BEAM[1],
        fontsize=14,
        ha='left', va='top',
        transform=ax_resmean_vs_thr.transAxes
    )

if hasPS:
    posy = 0.12
else:
    posy = 0.08
ax_resmean_vs_thr.text(
    TEXT_RES[0], TEXT_RES[1]-posy,
    ""+'Plotted on {}'.format(plot_date),
    fontsize=14,
    ha='left', va='top',
    transform=ax_resmean_vs_thr.transAxes
)
ax_resmean_vs_thr.text(0.02,0.015,
    "Association window radius: %s \u03BCm"%association_window + ". Plotting for thresholds above "+str(NSIGMANOISE)+"$\\times$noise RMS.",
    fontsize=10,
    ha='left', va='center',
    transform=ax_resmean_vs_thr.transAxes
)
ax_resmean_vs_thr.text(SETTING_RES[0],SETTING_RES[1],
                       CHIP_SETTINGS,
                       fontsize=12,
                       ha='left', va='top',
                       transform=ax_resmean_vs_thr.transAxes
                       )

fig_eff_vs_thr.savefig('plots/ALICE-ITS3_2023-03-24_APTS-SF_efficiency_vs_threshold_' +
                       FILE_SUFFIX+'.png', dpi=600)

fig_resmean_vs_thr.savefig('plots/ALICE-ITS3_2023-03-24_APTS-SF_efficiency_vs_threshold_' +
                       FILE_SUFFIX+'.png', dpi=600)

fig_eff_vs_thr.savefig('plots/ALICE-ITS3_2023-03-24_APTS-SF_resolution_vs_threshold_' +
                       FILE_SUFFIX+'.pdf', dpi=600)

fig_resmean_vs_thr.savefig('plots/ALICE-ITS3_2023-03-24_APTS-SF_resolution_vs_threshold_' +
                       FILE_SUFFIX+'.pdf', dpi=600)
