from pytz import country_timezones
import ROOT
import re
import argparse
from os import walk
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np

parser = argparse.ArgumentParser()


parser.add_argument('-pitch', '--pitch', help='Fixed value of the pixel pitch', action='store', default=15)
parser.add_argument('-thr', '--thr', help='Fixed value of threshold_seed', action='store', default="all")
parser.add_argument('-sca', '--sca', help='Fixed value of spatial_cut_abs', action='store', default=20)
parser.add_argument('-ice', '--ice', help='Fixed value of inpixel_cut_edge', action='store', default=0)
parser.add_argument('-nb', '--nb', help='Fixed value of the baseline', action='store', default=98)
parser.add_argument('-frm', '--frm', help='Fixed value of window frame', action='store', default=105)
args = parser.parse_args()

iter_val = -1
counter = 0
print("SETTTINGS:")
for key,value in vars(args).items():
    print(key," = ",value)
    if value == "all":
        iter_val = counter
        break
    counter += 1
if iter_val == -1:
    print("ERROR: no variable with all")
    exit()

THR = str(args.thr) 
SCA = str(args.sca) 
ICE = str(args.ice) 
NB = str(args.nb) 
FRAME = str(args.frm) 
PITCH = str(args.pitch)

list_of_xtitles = [
                    "pixel pitch (um)",
                    "threshold_seed (ADCu)",
                    "spatial_cut_abs (um)",
                    "inpixel_cut_edge (um)",
                    "frame for the baseline estimation",
                    "window frame upper edge",
                  ]

list_of_filenames = [
                    "Pitch",
                    "Threshold_seed",
                    "Spatial_cut_abs",
                    "Inpixel_cut_edge",
                    "Baseline",
                    "Frame",
                  ]

directory = "/home/giacomo/its-corryvreckan-tools/output/run0000"+PITCH+"/"


files = next(walk(directory), (None, None, []))[2]  # [] if no file
selected_files = []

for candidate_file in files:

    if ".root" not in candidate_file:
        continue
    if "analyseDUT_" not in candidate_file:
        continue

    settings = re.findall(r'\d+', candidate_file)
    if len(settings) != 6:
        continue
    counter = 0
    rejected = False
    for setting,var in zip(settings,vars(args).items()):
        if str(setting) != str(var[1]) and counter != iter_val:
            rejected = True
            break
        counter += 1
    if not rejected:
        selected_files.append([candidate_file,settings])

def take_element(list_to_sort):
     nested_list = list_to_sort[1]
     return int(nested_list[iter_val])
sorted_selected_files = sorted(selected_files, key=take_element)

if len(sorted_selected_files) == 0:
    print("ERROR: no file with this settings")
else:
    eff = []
    var = []
    errEffl = []
    errEffh = []
    for sel_file in sorted_selected_files:
        results = ROOT.TFile(directory+sel_file[0],"open")
        efficiency = results.Get("AnalysisEfficiency/APTS_4/eTotalEfficiency_inPixelROI")
        settings = re.findall(r'\d+', candidate_file)
        var.append(float(sel_file[1][iter_val]))
        eff.append(efficiency.GetEfficiency(1))
        errEffl.append(efficiency.GetEfficiencyErrorLow(1))
        errEffh.append(efficiency.GetEfficiencyErrorUp(1))

    print("x: ",var)
    print("y: ",eff)
    print("errl: ",errEffl)
    print("errh: ",errEffh)

    fig, ax1 = plt.subplots(figsize=(11,5))
    plt.subplots_adjust(left=0.07,right=0.75,top=0.95)

    asymmetric_error = [errEffl, errEffh]

    ax1.errorbar(var, eff, yerr=asymmetric_error, marker="s", linestyle='', color='tab:purple')


    ax1.set_ylabel('Efficiency')
    ax1.set_xlabel(list_of_xtitles[iter_val])
    ax1.grid()
    ax1.legend(loc='lower right',bbox_to_anchor =(1.32, -0.02),prop={"size":9})
    if THR == "all":
        x = 0.8
        y = 0.99
    else:
        x = 0.7
        y = 0.6

    ax1.text(
        x,y,
        '$\\bf{ITS3}$ beam test $\\it{preliminary}$',
        fontsize=12,
        ha='center', va='top',
        transform=ax1.transAxes
    )

    ax1.text(
        x,y-0.06,
        '@PS June 2022, 10 GeV/c protons',
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
    fig.savefig(directory+'efficiencyVs'+list_of_filenames[iter_val]+'.png', dpi=800)
    plt.show()


TXT_FILE = "results_pitch_"+PITCH+"_thr_"+THR+"_sca_"+SCA+"_ice_"+ICE+"_nb_"+NB+"_frame_"+FRAME+".txt"
with open(TXT_FILE, 'w') as fp:
    for val in var:
        # write each item on a new line
        fp.write("%s\n" % val)
    for val in eff:
        # write each item on a new line
        fp.write("%s\n" % val)
    for val in errEffl:
        # write each item on a new line
        fp.write("%s\n" % val)
    for val in errEffh:
        # write each item on a new line
        fp.write("%s\n" % val)