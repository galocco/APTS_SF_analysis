import matplotlib.pyplot as plt
import math
import argparse
import yaml
import os
import re
import utils
import numpy as np
import json
from matplotlib.ticker import FuncFormatter
from copy import copy
from matplotlib.ticker import FixedLocator, FixedFormatter

from matplotlib import rcParams
from cycler import cycler
import matplotlib.style as style
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
    "v_down":  "v",
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
TITLES = params['TITLES']
LABELS = params['LABELS']
VARIABLE = params['VARIABLE']
HAS_THR_ERR = params['HAS_THR_ERR']
corr = 1
if HAS_THR_ERR:
    corr = 0
# Define the ratios for width and height of subplots
width_ratios = [1, 1, 1, 1]  # Adjust as needed
height_ratios = [0.7, 0.7, 0.7]      # Adjust as needed

rows = 3
columns = 4
# Create a 3x4 grid of subplots with adjusted sizes
fig, axes = plt.subplots(rows, columns, figsize=(12, 9),
                         gridspec_kw={'width_ratios': width_ratios, 'height_ratios': height_ratios})

data_list_res_bin = [[],[],[],[]]
data_list_res_bin_err_up = [[],[],[],[]]
data_list_res_bin_err_lo = [[],[],[],[]]

data_list_res_analog = [[],[],[],[]]
data_list_res_analog_err_up = [[],[],[],[]]
data_list_res_analog_err_lo = [[],[],[],[]]

data_list_res_bin99 = [[],[],[],[]]
data_list_res_bin99_err_up = [[],[],[],[]]
data_list_res_bin99_err_lo = [[],[],[],[]]

data_list_res_analog99 = [[],[],[],[]]
data_list_res_analog99_err_up = [[],[],[],[]]
data_list_res_analog99_err_lo = [[],[],[],[]]

data_list_res_bin100 = [[],[],[],[]]
data_list_res_bin100_err_up = [[],[],[],[]]
data_list_res_bin100_err_lo = [[],[],[],[]]

data_list_res_analog100 = [[],[],[],[]]
data_list_res_analog100_err_up = [[],[],[],[]]
data_list_res_analog100_err_lo = [[],[],[],[]]

data_list_clu_100 = [[],[],[],[]]
data_list_clu_100_err_up = [[],[],[],[]]
data_list_clu_100_err_lo = [[],[],[],[]]

data_list_clu_noise = [[],[],[],[]]
data_list_clu_noise_err_up = [[],[],[],[]]
data_list_clu_noise_err_lo = [[],[],[],[]]

data_list_clu_eff99 = [[],[],[],[]]
data_list_clu_eff99_err_up = [[],[],[],[]]
data_list_clu_eff99_err_lo = [[],[],[],[]]

data_list_eff = [[],[],[],[]]
data_list_eff_err_up = [[],[],[],[]]
data_list_eff_err_lo = [[],[],[],[]]

data_list_eff_100 = [[],[],[],[]]
data_list_eff_100_err_up = [[],[],[],[]]
data_list_eff_100_err_lo = [[],[],[],[]]

data_list_thr = [[],[],[],[]]
data_list_thr_err_up = [[],[],[],[]]
data_list_thr_err_lo = [[],[],[],[]]

data_list_thr_first = [[],[],[],[]]
data_list_thr_first_err_up = [[],[],[],[]]
data_list_thr_first_err_lo = [[],[],[],[]]

xvals = [[],[],[],[]]
xvals99 = [[],[],[],[]]
xvals100 = [[],[],[],[]]

xlabels = []
xlims = []
xscales = []
index_var = 0

for var in VARIABLE:
    if var == "pitch":
        xlabels.append('Pitch (\u03BCm)')
        xlims.append([5,30])
        xscales.append('linear')
    elif  var == "vsub":
        xlabels.append(r'V$_{sub}$ (V)')
        xlims.append([-0.1, 4.9])
        xscales.append('linear')
    elif  var == "irrad":
        #xlabels.append(r'NIEL (1 MeV $n_{eq} cm^{-2})$')
        xlabels.append(r'Irradiation')
        xlims.append([0.5*10**12,10**15*5])
        xscales.append('linear')
        
    index_label = 0
    for label in LABELS[index_var]:
        data_list_clu_eff99[index_var].append([])
        data_list_clu_eff99_err_up[index_var].append([])
        data_list_clu_eff99_err_lo[index_var].append([])

        data_list_clu_noise[index_var].append([])
        data_list_clu_noise_err_up[index_var].append([])
        data_list_clu_noise_err_lo[index_var].append([])

        data_list_clu_100[index_var].append([])
        data_list_clu_100_err_up[index_var].append([])
        data_list_clu_100_err_lo[index_var].append([])

        data_list_res_bin[index_var].append([])
        data_list_res_bin_err_up[index_var].append([])
        data_list_res_bin_err_lo[index_var].append([])

        data_list_res_analog[index_var].append([])
        data_list_res_analog_err_up[index_var].append([])
        data_list_res_analog_err_lo[index_var].append([])

        data_list_res_bin99[index_var].append([])
        data_list_res_bin99_err_up[index_var].append([])
        data_list_res_bin99_err_lo[index_var].append([])

        data_list_res_analog99[index_var].append([])
        data_list_res_analog99_err_up[index_var].append([])
        data_list_res_analog99_err_lo[index_var].append([])

        data_list_res_bin100[index_var].append([])
        data_list_res_bin100_err_up[index_var].append([])
        data_list_res_bin100_err_lo[index_var].append([])

        data_list_res_analog100[index_var].append([])
        data_list_res_analog100_err_up[index_var].append([])
        data_list_res_analog100_err_lo[index_var].append([])

        data_list_eff[index_var].append([])
        data_list_eff_err_up[index_var].append([])
        data_list_eff_err_lo[index_var].append([])

        data_list_eff_100[index_var].append([])
        data_list_eff_100_err_up[index_var].append([])
        data_list_eff_100_err_lo[index_var].append([])

        data_list_thr[index_var].append([])
        data_list_thr_err_up[index_var].append([])
        data_list_thr_err_lo[index_var].append([])

        data_list_thr_first[index_var].append([])
        data_list_thr_first_err_up[index_var].append([])
        data_list_thr_first_err_lo[index_var].append([])

        xvals[index_var].append([])
        xvals99[index_var].append([])
        xvals100[index_var].append([])
        for chip in CHIPS[index_var][index_label]:
            f = open("data/paper_backup/"+chip+".json")
            chip_data = json.load(f)
            data_list_eff[index_var][index_label].append(chip_data["efficiency"][0])
            data_list_eff_err_up[index_var][index_label].append(chip_data["err_eff_up"][0])
            data_list_eff_err_lo[index_var][index_label].append(chip_data["err_eff_low"][0])

            data_list_res_bin[index_var][index_label].append(chip_data["resolutions_binary"][0])
            data_list_res_bin_err_up[index_var][index_label].append(chip_data["err_resolutions_binary"][0])
            data_list_res_bin_err_lo[index_var][index_label].append(chip_data["err_resolutions_binary"][0])

            data_list_res_analog[index_var][index_label].append(chip_data["resolutions_cluster"][0])
            data_list_res_analog_err_up[index_var][index_label].append(chip_data["err_resolutions_cluster"][0])
            data_list_res_analog_err_lo[index_var][index_label].append(chip_data["err_resolutions_cluster"][0])

            data_list_clu_noise[index_var][index_label].append(chip_data["clustersize"][0])
            data_list_clu_noise_err_up[index_var][index_label].append(chip_data["err_clustersize"][0])
            data_list_clu_noise_err_lo[index_var][index_label].append(chip_data["err_clustersize"][0])

            data_list_thr_first[index_var][index_label].append(chip_data["threshold"][0]/utils.hundredElectronToADCu[chip_data["chip"]]*100)
            data_list_thr_first_err_up[index_var][index_label].append(1/utils.hundredElectronToADCu[chip_data["chip"]]*100*corr)
            data_list_thr_first_err_lo[index_var][index_label].append(1/utils.hundredElectronToADCu[chip_data["chip"]]*100*corr)
            has99eff = False
            try:
                thr = chip_data["thr_eff99"]
            except KeyError:
                thr = "None"

            if thr !="None" and chip_data["thr_eff99"]>=chip_data["threshold"][0]:
                has99eff = True
                data_list_thr[index_var][index_label].append(chip_data["thr_eff99"]/utils.hundredElectronToADCu[chip_data["chip"]]*100)
                data_list_thr_err_up[index_var][index_label].append(chip_data["err_thr_eff99_up"]/utils.hundredElectronToADCu[chip_data["chip"]]*100*corr)
                data_list_thr_err_lo[index_var][index_label].append(chip_data["err_thr_eff99_low"]/utils.hundredElectronToADCu[chip_data["chip"]]*100*corr)

                index_99 = chip_data["threshold"].index(chip_data["thr_eff99"])
                data_list_clu_eff99[index_var][index_label].append(chip_data["clustersize"][index_99])
                data_list_clu_eff99_err_up[index_var][index_label].append(chip_data["err_clustersize"][index_99])
                data_list_clu_eff99_err_lo[index_var][index_label].append(chip_data["err_clustersize"][index_99])

                data_list_res_bin99[index_var][index_label].append(chip_data["resolutions_binary"][index_99])
                data_list_res_bin99_err_up[index_var][index_label].append(chip_data["err_resolutions_binary"][index_99])
                data_list_res_bin99_err_lo[index_var][index_label].append(chip_data["err_resolutions_binary"][index_99])

                data_list_res_analog99[index_var][index_label].append(chip_data["resolutions_cluster"][index_99])
                data_list_res_analog99_err_up[index_var][index_label].append(chip_data["err_resolutions_cluster"][index_99])
                data_list_res_analog99_err_lo[index_var][index_label].append(chip_data["err_resolutions_cluster"][index_99])
            
            delta = 1.00E10
            index_100 = 0
            has100eff = False
            for thr in chip_data["threshold"]:
                new_delta = math.fabs(thr/utils.hundredElectronToADCu[chip_data["chip"]]*100-100)
                if new_delta<delta:
                    delta = new_delta
                    index_100 = chip_data["threshold"].index(thr)
            if chip_data["threshold"][0]/utils.hundredElectronToADCu[chip_data["chip"]]*100 < 98:
                has100eff = True
                
                data_list_eff_100[index_var][index_label].append(chip_data["efficiency"][index_100])
                data_list_eff_100_err_up[index_var][index_label].append(chip_data["err_eff_up"][index_100])
                data_list_eff_100_err_lo[index_var][index_label].append(chip_data["err_eff_low"][index_100])

                data_list_clu_100[index_var][index_label].append(chip_data["clustersize"][index_100])
                data_list_clu_100_err_up[index_var][index_label].append(chip_data["err_clustersize"][index_100])
                data_list_clu_100_err_lo[index_var][index_label].append(chip_data["err_clustersize"][index_100])

                data_list_res_bin100[index_var][index_label].append(chip_data["resolutions_binary"][index_100])
                data_list_res_bin100_err_up[index_var][index_label].append(chip_data["err_resolutions_binary"][index_100])
                data_list_res_bin100_err_lo[index_var][index_label].append(chip_data["err_resolutions_binary"][index_100])

                data_list_res_analog100[index_var][index_label].append(chip_data["resolutions_cluster"][index_100])
                data_list_res_analog100_err_up[index_var][index_label].append(chip_data["err_resolutions_cluster"][index_100])
                data_list_res_analog100_err_lo[index_var][index_label].append(chip_data["err_resolutions_cluster"][index_99])
                            


            if var == "pitch":
                xval = float(re.findall(r'\d+', chip_data["chip"])[0]) 
            elif  var == "vsub":
                xval = float(re.findall(r'\d+\.\d+', chip_data["chip"])[0])
            elif  var == "irrad":
                xval_row = re.findall(r'[0-9]*\.[0-9]+E[+-][0-9]+', chip_data["chip"])
                if xval_row == []:
                    xval = 0
                elif ".00E+" in xval_row[0]:
                    xval = math.log10(float(xval_row[0]))-12
                if "300Mrad" in chip_data["chip"]:
                    xval = 4

            xvals[index_var][index_label].append(xval)
            if has99eff:
                xvals99[index_var][index_label].append(xval)
            if has100eff:
                xvals100[index_var][index_label].append(xval)
        index_label += 1
    index_var+=1

# Now you can plot on each subplot
ax_first = []
ax_dummy = []
ax_dummy_2 = []
for i in range(rows):
    for j in range(columns):
        ax = axes[i, j]  # Get the current axis

        ax_dummy.append(ax.twiny())
        ax_dummy_2.append(ax.twiny())

        ax_dummy_2[4*i+j].xaxis.set_tick_params(top=False)
        ax_dummy_2[4*i+j].xaxis.set_tick_params(labeltop=False)
        ax_dummy[4*i+j].xaxis.set_tick_params(top=False)
        ax_dummy[4*i+j].xaxis.set_tick_params(labeltop=False)
        if i == 2:
            ax_first.append(ax.twiny())
            ax_first[j].xaxis.set_tick_params(top=False)
            ax_first[j].xaxis.set_tick_params(labeltop=False)

        if i<2:
            ax.axhline(99, linestyle='dashed', color='grey')
            if VARIABLE[j] == "pitch":
                ax.text(8.5, 99, "99", fontsize=8, ha='right', va='center')
            elif VARIABLE[j] == "vsub":
                ax.text(-0.5, 99, "99", fontsize=8, ha='right', va='center')
            elif VARIABLE[j] == "irrad":
                ax.text(-0.3, 99, "99", fontsize=8, ha='right', va='center')


        if i ==0:
            for data, err_up, err_lo,x in zip(data_list_eff[j], data_list_eff_err_up[j], data_list_eff_err_lo[j], xvals[j]):
                index4 = -1
                if VARIABLE[j] == "irrad" and 4 in x:
                    index4 =  x.index(4)
                x_tmp = copy(x)
                if index4 != -1:
                    datapop = data.pop(index4)
                    errpop_up = err_up.pop(index4)
                    errpop_lo = err_lo.pop(index4)
                    xpop = x_tmp.pop(index4)
                    asymmetric_error_y = [[errpop_lo],[errpop_up]]
                    ax_dummy[i*4+j].errorbar([4], [datapop], yerr=asymmetric_error_y, color= "#E69F00", marker ="v")

                asymmetric_error_y = [err_lo,err_up]
                ax.errorbar(x_tmp, data, yerr=asymmetric_error_y)
        elif i ==1:
            for data, err_up, err_lo,x in zip(data_list_eff_100[j], data_list_eff_100_err_up[j], data_list_eff_100_err_lo[j], xvals100[j]):
                index4 = -1
                if VARIABLE[j] == "irrad" and 4 in x:
                    index4 =  x.index(4)
                x_tmp = copy(x)
                if index4 != -1:
                    datapop = data.pop(index4)
                    errpop_up = err_up.pop(index4)
                    errpop_lo = err_lo.pop(index4)
                    xpop = x_tmp.pop(index4)
                    asymmetric_error_y = [[errpop_lo],[errpop_up]]
                    ax_dummy[i*4+j].errorbar([4], [datapop], yerr=asymmetric_error_y, color= "#E69F00", marker ="v")

                asymmetric_error_y = [err_lo,err_up]
                ax.errorbar(x_tmp, data, yerr=asymmetric_error_y)
        else:
            if j ==0:
                ax.errorbar([], [], ([], []), label="Efficiency = 99%",
                                        marker='s', elinewidth=1.3, capsize=1.5, color='dimgrey')
                ax.errorbar([], [], ([], []), label=r'3RMS$_{noise}$',
                                        marker='s', linestyle='dotted', elinewidth=1.3, capsize=1.5, color='dimgrey', mfc='w')
                
            for data, err_up, err_lo,x,label in zip(data_list_thr[j], data_list_thr_err_up[j], data_list_thr_err_lo[j], xvals99[j],LABELS[j]):
                index4 = -1
                if VARIABLE[j] == "irrad" and 4 in x:
                    index4 =  x.index(4)

                x_tmp = copy(x)
                if index4 != -1:
                    datapop = data.pop(index4)
                    errpop_up = err_up.pop(index4)
                    errpop_lo = err_lo.pop(index4)
                    xpop = x_tmp.pop(index4)
                    asymmetric_error_y = [[errpop_lo],[errpop_up]]
                    ax_dummy[i*4+j].errorbar([4], [datapop], yerr=asymmetric_error_y, color= "#E69F00", marker ="v")
                asymmetric_error_y = [err_lo, err_up]
                ax.errorbar(x_tmp, data, yerr=asymmetric_error_y, label= label)

            for data, err_up, err_lo,x in zip(data_list_thr_first[j], data_list_thr_first_err_up[j], data_list_thr_first_err_lo[j], xvals[j]):
                index4 = -1
                if VARIABLE[j] == "irrad" and 4 in x:
                    index4 =  x.index(4)

                x_tmp = copy(x)
                if index4 != -1:
                    datapop = data.pop(index4)
                    errpop_up = err_up.pop(index4)
                    errpop_lo = err_lo.pop(index4)
                    xpop = x_tmp.pop(index4)
                    asymmetric_error_y = [[errpop_lo],[errpop_up]]
                    ax_dummy_2[i*4+j].errorbar([4], [datapop], yerr=asymmetric_error_y, mfc='w', color= "#E69F00", marker ="v")
                asymmetric_error_y = [err_lo, err_up]
                ax_first[j].errorbar(x_tmp, data, yerr=asymmetric_error_y, linestyle="dotted", mfc='w')

        ax.grid()
        if j == 0:
            if i == 0:
                ax.set_ylabel('Detection efficiency (%) \nthr = '+r'3RMS$_{noise}$')  # Set the y-axis label
            elif i == 1:
                ax.set_ylabel('Detection efficiency (%) \nthr = 100 '+r'e$_{-}$')  # Set the y-axis label
            else:
                #ax.set_ylabel(r'Threshold$_{eff = 99\%}$ (e$^{-}$) ')  # Set the y-axis label
                ax.set_ylabel(r'Threshold (e$^{-}$) ')  # Set the y-axis label
                
        if i == 0:
            ax.set_title(TITLES[j])
            ax.set_ylim(91, 101)
        elif i == 1:
            ax.set_ylim(91, 101)
        elif i == 2:
            ax.set_ylim(59, 221)
            ax_first[j].set_ylim(59, 221)
        ax.set_xlabel(xlabels[j])  # Set the y-axis label
       # ax.set_xlim(xlims[j][0],xlims[j][1])
        ax.set_xscale(xscales[j])

# Adjust layout spacing
plt.tight_layout()
plt.subplots_adjust(bottom=0.2)  # Adjust the value as needed
for i in range(0,rows):
    for j in range(0,columns):
        if VARIABLE[j] == "irrad":
            custom_labels = ['0', r'$10^{13}$', r'$10^{14}$', r'$10^{15}$', r'300 Mrad']
            custom_labels = ['Non-irradiated', r'$10^{13}$ NIEL', r'$10^{14}$ NIEL', r'$10^{15}$ NIEL', r'300 Mrad']

            x = [0,1,2,3,4]
            axes[i, j].set_xlim(-0.2,4.2)
            # Create a FixedLocator for the custom tick positions
            locator = FixedLocator(x)

            # Use FixedLocator and FixedFormatter together
            axes[i, j].xaxis.set_major_locator(locator)
            axes[i, j].xaxis.set_major_formatter(FixedFormatter(custom_labels))
            axes[i, j].set_xticklabels(custom_labels, rotation=-15)
            if i == 1:
                ax_first[j].set_xlim(-0.2,4.2)
                ax_first[j].xaxis.set_major_locator(locator)
                ax_first[j].xaxis.set_major_formatter(FixedFormatter(custom_labels))
            ax_dummy[i*4+j].set_xlim(-0.2,4.2)
            ax_dummy_2[i*4+j].set_xlim(-0.2,4.2)
        if VARIABLE[j] == "vsub":
            custom_labels = ['0', '1.2','2.4','3.6','4.8']
            x = [0, 1.2,2.4,3.6,4.8]
            axes[i, j].set_xlim(-0.25,5.05)
            # Create a FixedLocator for the custom tick positions
            locator = FixedLocator(x)

            # Use FixedLocator and FixedFormatter together
            axes[i,j].xaxis.set_major_locator(locator)
            axes[i,j].xaxis.set_major_formatter(FixedFormatter(custom_labels))
            #ax_first[j].xaxis.set_major_locator(locator)
            #ax_first[j].xaxis.set_major_formatter(FixedFormatter(custom_labels))
        if VARIABLE[j] == "pitch":
            axes[i, j].set_xlim(9.25,25.75)
            if i == 1:
                ax_first[j].set_xlim(9.25,25.75)

# Create a common legend for the bottom row
bottom_axes = axes[rows-1, :]
for ax in bottom_axes:
    bottom_legend = ax.legend(bbox_to_anchor=(0.75, -0.55), loc='lower right')
    ax.add_artist(bottom_legend)

# Show the plot
plt.savefig("eff"+FILE_SUFFIX+".png")

rows = 6
columns = 4
# Create a 3x4 grid of subplots with adjusted sizes
fig, axes = plt.subplots(rows, columns, figsize=(12, rows*4))
ax_analog = [[],[],[]]

ax_dummy = []
ax_dummy_2 = []
# Now you can plot on each subplot
for i in range(rows):
    for j in range(columns):
        ax = axes[i, j]  # Get the current axis
        ax_dummy.append(ax.twiny())
        ax_dummy_2.append(ax.twiny())

        ax_dummy_2[4*i+j].xaxis.set_tick_params(top=False)
        ax_dummy_2[4*i+j].xaxis.set_tick_params(labeltop=False)
        ax_dummy[4*i+j].xaxis.set_tick_params(top=False)
        ax_dummy[4*i+j].xaxis.set_tick_params(labeltop=False)
        if i < 3:
            ax_analog[i].append(ax.twiny())
            ax_analog[i][j].xaxis.set_tick_params(top=False)
            ax_analog[i][j].xaxis.set_tick_params(labeltop=False)

        if i ==0:
            for data, err_up, err_lo,x in zip(data_list_res_bin[j], data_list_res_bin_err_up[j], data_list_res_bin_err_lo[j], xvals[j]):
                index4 = -1
                if VARIABLE[j] == "irrad" and 4 in x:
                    index4 =  x.index(4)

                x_tmp = copy(x)
                if index4 != -1:
                    datapop = data.pop(index4)
                    errpop_up = err_up.pop(index4)
                    errpop_lo = err_lo.pop(index4)
                    xpop = x_tmp.pop(index4)
                    asymmetric_error_y = [[errpop_lo],[errpop_up]]
                    ax_dummy[i*4+j].errorbar([4], [datapop], yerr=asymmetric_error_y, color= "#E69F00", marker ="v")
                asymmetric_error_y = [err_lo, err_up]
                ax.errorbar(x_tmp, data, yerr=asymmetric_error_y)

            for data, err_up, err_lo,x,label in zip(data_list_res_analog[j], data_list_res_analog_err_up[j], data_list_res_analog_err_lo[j], xvals[j],LABELS[j]):
                index4 = -1
                if VARIABLE[j] == "irrad" and 4 in x:
                    index4 =  x.index(4)

                x_tmp = copy(x)
                if index4 != -1:
                    datapop = data.pop(index4)
                    errpop_up = err_up.pop(index4)
                    errpop_lo = err_lo.pop(index4)
                    xpop = x_tmp.pop(index4)
                    asymmetric_error_y = [[errpop_lo],[errpop_up]]
                    ax_dummy[i*4+j].errorbar([4], [datapop], yerr=asymmetric_error_y, color= "#E69F00", marker ="v", mfc='w')
                asymmetric_error_y = [err_lo, err_up]
                ax_analog[i][j].errorbar(x_tmp, data, yerr=asymmetric_error_y, linestyle='dotted', mfc='w')
        elif i == 1:
            for data, err_up, err_lo,x in zip(data_list_res_bin99[j], data_list_res_bin99_err_up[j], data_list_res_bin99_err_lo[j], xvals99[j]):
                index4 = -1
                if VARIABLE[j] == "irrad" and 4 in x:
                    index4 =  x.index(4)

                x_tmp = copy(x)
                if index4 != -1:
                    datapop = data.pop(index4)
                    errpop_up = err_up.pop(index4)
                    errpop_lo = err_lo.pop(index4)
                    xpop = x_tmp.pop(index4)
                    asymmetric_error_y = [[errpop_lo],[errpop_up]]
                    ax_dummy[i*4+j].errorbar([4], [datapop], yerr=asymmetric_error_y, color= "#E69F00", marker ="v")
                asymmetric_error_y = [err_lo, err_up]
                ax.errorbar(x_tmp, data, yerr=asymmetric_error_y)

            for data, err_up, err_lo,x,label in zip(data_list_res_analog99[j], data_list_res_analog99_err_up[j], data_list_res_analog99_err_lo[j], xvals99[j],LABELS[j]):
                index4 = -1
                if VARIABLE[j] == "irrad" and 4 in x:
                    index4 =  x.index(4)

                x_tmp = copy(x)
                if index4 != -1:
                    datapop = data.pop(index4)
                    errpop_up = err_up.pop(index4)
                    errpop_lo = err_lo.pop(index4)
                    xpop = x_tmp.pop(index4)
                    asymmetric_error_y = [[errpop_lo],[errpop_up]]
                    ax_dummy[i*4+j].errorbar([4], [datapop], yerr=asymmetric_error_y, color= "#E69F00", marker ="v", mfc='w')
                asymmetric_error_y = [err_lo, err_up]
                ax_analog[i][j].errorbar(x_tmp, data, yerr=asymmetric_error_y, linestyle='dotted', mfc='w')

        elif i == 2:
            for data, err_up, err_lo,x in zip(data_list_res_bin100[j], data_list_res_bin100_err_up[j], data_list_res_bin100_err_lo[j], xvals100[j]):
                index4 = -1
                if VARIABLE[j] == "irrad" and 4 in x:
                    index4 =  x.index(4)

                x_tmp = copy(x)
                if index4 != -1:
                    datapop = data.pop(index4)
                    errpop_up = err_up.pop(index4)
                    errpop_lo = err_lo.pop(index4)
                    xpop = x_tmp.pop(index4)
                    asymmetric_error_y = [[errpop_lo],[errpop_up]]
                    ax_dummy[i*4+j].errorbar([4], [datapop], yerr=asymmetric_error_y, color= "#E69F00", marker ="v")
                asymmetric_error_y = [err_lo, err_up]
                ax.errorbar(x_tmp, data, yerr=asymmetric_error_y)

            for data, err_up, err_lo,x,label in zip(data_list_res_analog100[j], data_list_res_analog100_err_up[j], data_list_res_analog100_err_lo[j], xvals100[j],LABELS[j]):
                index4 = -1
                if VARIABLE[j] == "irrad" and 4 in x:
                    index4 =  x.index(4)

                x_tmp = copy(x)
                if index4 != -1:
                    datapop = data.pop(index4)
                    errpop_up = err_up.pop(index4)
                    errpop_lo = err_lo.pop(index4)
                    xpop = x_tmp.pop(index4)
                    asymmetric_error_y = [[errpop_lo],[errpop_up]]
                    ax_dummy[i*4+j].errorbar([4], [datapop], yerr=asymmetric_error_y, color= "#E69F00", marker ="v", mfc='w')
                asymmetric_error_y = [err_lo, err_up]
                ax_analog[i][j].errorbar(x_tmp, data, yerr=asymmetric_error_y, linestyle='dotted', mfc='w')

                

        elif i == 3:
            for data, err_up, err_lo,x,label in zip(data_list_clu_noise[j], data_list_clu_noise_err_up[j], data_list_clu_noise_err_lo[j], xvals[j],LABELS[j]):
                index4 = -1
                if VARIABLE[j] == "irrad" and 4 in x:
                    index4 =  x.index(4)

                x_tmp = copy(x)
                if index4 != -1:
                    datapop = data.pop(index4)
                    errpop_up = err_up.pop(index4)
                    errpop_lo = err_lo.pop(index4)
                    xpop = x_tmp.pop(index4)
                    asymmetric_error_y = [[errpop_lo],[errpop_up]]
                    ax_dummy[i*4+j].errorbar([4], [datapop], yerr=asymmetric_error_y, color= "#E69F00", marker ="v")
                asymmetric_error_y = [err_lo, err_up]
                ax.errorbar(x_tmp, data, yerr=asymmetric_error_y, label= label)
        elif i == 4:
            for data, err_up, err_lo,x,label in zip(data_list_clu_eff99[j], data_list_clu_eff99_err_up[j], data_list_clu_eff99_err_lo[j], xvals99[j],LABELS[j]):
                index4 = -1
                if VARIABLE[j] == "irrad" and 4 in x:
                    index4 =  x.index(4)

                x_tmp = copy(x)
                if index4 != -1:
                    datapop = data.pop(index4)
                    errpop_up = err_up.pop(index4)
                    errpop_lo = err_lo.pop(index4)
                    xpop = x_tmp.pop(index4)
                    asymmetric_error_y = [[errpop_lo],[errpop_up]]
                    ax_dummy[i*4+j].errorbar([4], [datapop], yerr=asymmetric_error_y, color= "#E69F00", marker ="v")
                asymmetric_error_y = [err_lo, err_up]
                ax.errorbar(x_tmp, data, yerr=asymmetric_error_y, label= label)
        elif i == 5:
            if j ==0:
                ax.errorbar([], [], ([], []), label="Hit/no-hit spatial resolution",
                                        marker='s', elinewidth=1.3, capsize=1.5, color='dimgrey')
                ax.errorbar([], [], ([], []), label="Analogue spatial resolution",
                                        marker='s', linestyle='dotted', elinewidth=1.3, capsize=1.5, color='dimgrey', mfc='w')
            
            for data, err_up, err_lo,x,label in zip(data_list_clu_100[j], data_list_clu_100_err_up[j], data_list_clu_100_err_lo[j], xvals100[j],LABELS[j]):
                index4 = -1
                if VARIABLE[j] == "irrad" and 4 in x:
                    index4 =  x.index(4)

                x_tmp = copy(x)
                if index4 != -1:
                    datapop = data.pop(index4)
                    errpop_up = err_up.pop(index4)
                    errpop_lo = err_lo.pop(index4)
                    xpop = x_tmp.pop(index4)
                    asymmetric_error_y = [[errpop_lo],[errpop_up]]
                    ax_dummy[i*4+j].errorbar([4], [datapop], yerr=asymmetric_error_y, color= "#E69F00", marker ="v")
                asymmetric_error_y = [err_lo, err_up]
                ax.errorbar(x_tmp, data, yerr=asymmetric_error_y, label= label)

        ax.grid()


        if j == 0:
            if i == 0:
                ax.set_ylabel('Spatial resolution (\u03BCm) \n thr = '+r'3RMS$_{noise}$')  # Set the y-axis label
            if i == 1:
                ax.set_ylabel('Spatial resolution (\u03BCm) \n thr '+r'eff = 99%')  # Set the y-axis label
            if i == 2:
                ax.set_ylabel('Spatial resolution (\u03BCm) \n thr '+r' = 100 e$^{-}$%')  # Set the y-axis label
            if i == 3:
                ax.set_ylabel('Average cluster size \n thr '+r'3RMS$_{noise}$')  # Set the y-axis label
            if i == 4:
                ax.set_ylabel('Average cluster size \n thr '+r'eff = 99%')  # Set the y-axis label
            if i == 5:
                ax.set_ylabel('Average cluster size \n thr '+r' = 100 e$^{-}$')  # Set the y-axis label
        if i == 0:
            ax.set_title(TITLES[j])
        if i>2:
            ax.set_ylim(0.95,3.05)
        ax.set_xlabel(xlabels[j])  # Set the y-axis label
        # ax.set_xlim(xlims[j][0],xlims[j][1])
        ax.set_xscale(xscales[j])


# Adjust layout spacing
plt.tight_layout()
plt.subplots_adjust(bottom=0.2)  # Adjust the value as needed

for i in range(0,rows):
    for j in range(0,columns):
        if VARIABLE[j] == "irrad":
            custom_labels = ['Non-irradiated', r'$10^{13}$ NIEL', r'$10^{14}$ NIEL', r'$10^{15}$ NIEL', r'300 Mrad']
            x = [0,1,2,3,4]

            axes[i, j].set_xlim(-0.2,4.2)
            # Create a FixedLocator for the custom tick positions
            locator = FixedLocator(x)

            # Use FixedLocator and FixedFormatter together
            axes[i, j].xaxis.set_major_locator(locator)
            axes[i, j].xaxis.set_major_formatter(FixedFormatter(custom_labels))
            axes[i, j].set_xticklabels(custom_labels, rotation=-15)
            if i < 3:
                ax_analog[i][j].set_xlim(-0.2,4.2)
                ax_analog[i][j].xaxis.set_major_locator(locator)
                ax_analog[i][j].xaxis.set_major_formatter(FixedFormatter(custom_labels))
            ax_dummy[i*4+j].set_xlim(-0.2,4.2)
            ax_dummy_2[i*4+j].set_xlim(-0.2,4.2)
        elif VARIABLE[j] == "vsub":
            custom_labels = ['0', '1.2','2.4','3.6','4.8']
            x = [0, 1.2,2.4,3.6,4.8]
            axes[i, j].set_xlim(-0.25,5.05)
            # Create a FixedLocator for the custom tick positions
            locator = FixedLocator(x)

            # Use FixedLocator and FixedFormatter together
            axes[i, j].xaxis.set_major_locator(locator)
            axes[i, j].xaxis.set_major_formatter(FixedFormatter(custom_labels))
            if i < 3:
                ax_analog[i][j].set_xlim(-0.25,5.05)
                ax_analog[i][j].xaxis.set_major_locator(locator)
                ax_analog[i][j].xaxis.set_major_formatter(FixedFormatter(custom_labels))
        elif VARIABLE[j] == "pitch":
            axes[i, j].set_xlim(9.25,25.75)
            if i < 3:
                ax_analog[i][j].set_xlim(9.25,25.75)

# Create a common legend for the bottom row
bottom_axes = axes[rows-1, :]
for ax in bottom_axes:
    bottom_legend = ax.legend(bbox_to_anchor=(0.8, -0.7), loc='lower right')
    ax.add_artist(bottom_legend)

# Show the plot
plt.savefig("res"+FILE_SUFFIX+".png")
