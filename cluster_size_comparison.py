from ROOT import TFile, TF1, TMath
import matplotlib as mpl
import matplotlib.pyplot as plt
import math
import argparse
import yaml
import os
import re

parser = argparse.ArgumentParser()
parser.add_argument('-l', '--limit',
                    help='Apply lower limit of e- range', action='store_true')
parser.add_argument("config", help="Path to the YAML configuration file")
args = parser.parse_args()

with open(os.path.expandvars(args.config), 'r') as stream:
    try:
        params = yaml.full_load(stream)
    except yaml.YAMLError as exc:
        print(exc)

use_limit = args.limit

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


# plot of the resolution (Average cluster size) vs thr
fig_resx_vs_thr, ax_resx_vs_thr = plt.subplots(figsize=(11, 5))
plt.subplots_adjust(left=0.07, right=0.75, top=0.95)
ax_cluster_size_x = ax_resx_vs_thr.twinx()
ax_resx_vs_thr.errorbar([], [], ([], []), label="Average cluster size", marker='o',
                        markerfacecolor='none', linestyle='dashed', elinewidth=1.3, capsize=1.5, color='dimgrey')

fit_info = TFile(plots_dir+"/fit_info.root", "recreate")

for file_path_list, noise_path, label, chip, color in zip(FILE_PATHS, NOISE_PATHS, LABELS, CHIPS, COLORS):
    sub_dir = fit_info.mkdir(label)
    err_clustersize_list = []
    
    fhr_file = TFile(noise_path, "read")
    
    if chip == "AF25P_W22_1.2V" or "June" in label:
        apts = "4"
    else:
        apts = "3"

    noise_values = fhr_file.Get(
        "EventLoaderEUDAQ2/APTS_"+apts+"/hPixelRawValues")

    eThrLimit = None
    if use_limit:
        eThrLimit = (noise_values.GetStdDev()*NSIGMANOISE)*100/hundredElectronToADCu[chip]
        print("plotting above ",eThrLimit," electrons")

    fhr_file.Close()

    for file_path in file_path_list:
        print(file_path)
        thr = int(re.findall(r'\d+', file_path)[-1])
        input_file = TFile(file_path, "read")
        clusterSize = input_file.Get(
            "AnalysisDUT/APTS_"+apts+"/clusterSizeAssociated")
            
        charge.append(100*thr/hundredElectronToADCu[chip])
        clustersize_list.append(clusterSize.GetMean())
        err_clustersize_list.append(clusterSize.GetMeanError())

    asymmetric_error_x = [err_res_low_x, err_res_up_x]
    ax_resx_vs_thr.errorbar(charge, res_list_x, yerr=asymmetric_error_x,
                            label=label, marker="s", linestyle='', color=color)
fig_eff_vs_thr.savefig(plots_dir+'/efficiencyVsThreshold_' +
                       FILE_SUFFIX+'_'+fit_label+'.png', dpi=600)