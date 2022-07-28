import re
import argparse
from os import walk
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np

parser = argparse.ArgumentParser()


parser.add_argument('-pitch', '--pitch', help='Fixed value of the pixel pitch', action='store', default="comp")
parser.add_argument('-fix', '--fix', help='Fixed variable', action='store', default="thr")
parser.add_argument('-ice', '--ice', help='Fixed value of inpixel_cut_edge', action='store', default=0)
parser.add_argument('-nb', '--nb', help='Fixed value of the baseline', action='store', default=98)
parser.add_argument('-frm', '--frm', help='Fixed value of window frame', action='store', default=105)
args = parser.parse_args()

iter_val = -1
comp_val = -1
counter = 0
print("SETTINGS:")
for key,value in vars(args).items():
    print(key," = ",value)
    if value == "comp":
        comp_val = counter
    counter += 1

if comp_val == -1:
    print("ERROR: no variable with comp")
    exit()
FIXED = args.fix
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

if FIXED== "sca":
    TXT_FILE_LIST = [
                    "results_pitch_10_thr_all_sca_15_ice_"+ICE+"_nb_"+NB+"_frame_"+FRAME+".txt",
                    "results_pitch_15_thr_all_sca_20_ice_"+ICE+"_nb_"+NB+"_frame_"+FRAME+".txt",
                    "results_pitch_20_thr_all_sca_25_ice_"+ICE+"_nb_"+NB+"_frame_"+FRAME+".txt",
                    "results_pitch_25_thr_all_sca_30_ice_"+ICE+"_nb_"+NB+"_frame_"+FRAME+".txt"
                    ]
    iter_val = 1
elif FIXED=="thr":
    TXT_FILE_LIST = [
                    "results_pitch_10_thr_80_sca_all_ice_"+ICE+"_nb_"+NB+"_frame_"+FRAME+".txt",
                    "results_pitch_15_thr_80_sca_all_ice_"+ICE+"_nb_"+NB+"_frame_"+FRAME+".txt",
                    "results_pitch_20_thr_80_sca_all_ice_"+ICE+"_nb_"+NB+"_frame_"+FRAME+".txt",
                    "results_pitch_25_thr_80_sca_all_ice_"+ICE+"_nb_"+NB+"_frame_"+FRAME+".txt"
                    ]
    iter_val = 2
else:
    TXT_FILE_LIST = [
                    "results_pitch_15_thr_all_sca_20_ice_0_nb_98_frame_102.txt",
                    "results_pitch_15_thr_all_sca_20_ice_0_nb_98_frame_105.txt",
                    "results_pitch_15_thr_all_sca_20_ice_0_nb_1_frame_200.txt",
                    "results_pitch_15_thr_all_sca_20_ice_0_nb_1_frame_105.txt",
                    "results_pitch_15_thr_all_sca_20_ice_0_nb_50_frame_105.txt"
                    ]
    iter_val = 1
    list_of_filenames[iter_val] += "_frame"

#work in progres to 
if False:
    dirßectory = "/home/giacomo/its-corryvreckan-tools/"

    files = next(walk(directory), (None, None, []))[2]  # [] if no file
    TXT_FILE_LIST = []

    for candidate_file in files:
        if ".txt" not in candidate_file:
            continue
        if "results_" not in candidate_file:
            continue

        settings = re.findall(r'\d+', candidate_file)
        if len(settings) != 5:
            continue
        counter = 0
        rejected = False
        pitch = settings[0]
        settings.pop(0)
        for setting,var in zip(settings,vars(args).items()):
            if counter == iter_val or counter == comp_val:
                continue
            if str(setting) != str(var[1]):
                rejected = True
                break
            counter += 1
        if not rejected:
            TXT_FILE_LIST.append([candidate_file,settings[0]])

print(TXT_FILE_LIST)
fig, ax1 = plt.subplots(figsize=(11,5))
plt.subplots_adjust(left=0.07,right=0.75,top=0.95)

for TXT_FILE in TXT_FILE_LIST:
    print(TXT_FILE)
    with open(TXT_FILE, 'r') as f:
        lines = f.readlines()
    n_meas = len(lines)/4
    x = []
    y = []
    eyl = []
    eyh = []
    counter = 0
    for line in lines:
        if counter // n_meas == 0:
            x.append(float(line.replace('\n', '')))
        elif counter // n_meas == 1:
            y.append(float(line.replace('\n', '')))
        elif counter // n_meas == 2:
            eyl.append(float(line.replace('\n', '')))
        elif counter // n_meas == 3:
            eyh.append(float(line.replace('\n', '')))
        counter += 1

    asymmetric_error = [eyl, eyh]
    pixel_pitch = re.findall(r'\d+', TXT_FILE)[0]
    label = 'pixel pitch = '+pixel_pitch+'um'
    if FIXED!= "thr" and FIXED != "sca":
        if re.findall(r'\d+', TXT_FILE)[-1] == "200":
            label = "Vmin in frames [1," +re.findall(r'\d+', TXT_FILE)[-1]+"], baseline = "+re.findall(r'\d+', TXT_FILE)[-2]
        elif re.findall(r'\d+', TXT_FILE)[-2] == "50":
            label = "Vmin in frames [99," +re.findall(r'\d+', TXT_FILE)[-1]+"], baseline = [1,90] (last week)"
        else:
            label = "Vmin in frames [99," +re.findall(r'\d+', TXT_FILE)[-1]+"], baseline = "+re.findall(r'\d+', TXT_FILE)[-2]
    ax1.errorbar(x, y, yerr=asymmetric_error, label=label, marker="s", linestyle='')

ax1.set_ylabel('Efficiency')
ax1.set_xlabel(list_of_xtitles[iter_val])
if FIXED == "sca" or FIXED == "all":
    ax1.legend(loc='lower left')
else:
    ax1.legend(loc='lower right')
ax1.grid()
#ax1.yscale("log")
ax1.set_ylim(0.69,1.01)

ax1.legend(loc='lower right',bbox_to_anchor =(1.32, -0.02),prop={"size":9})

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

fig.savefig('efficiencyVs'+list_of_filenames[iter_val]+'_comparison.png', dpi=800)
plt.show()