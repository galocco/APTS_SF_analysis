from distutils.archive_util import make_archive
import ROOT
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import re

def get_entries_in_range(hist, bin_min, bin_max):
    entries = 0
    for k in range(bin_min,bin_max+1):
        entries += hist.GetBinContent(k)
    return entries

directory = "/home/giacomo/its-corryvreckan-tools/output/run000015/"

list_of_files = [
                    "analyseDUT_15_thr_80_sca_20_ice_0_nb_48_55.root",
                    "analyseDUT_15_thr_80_sca_20_ice_0_nb_1_55.root"
                ]

list_of_labels = [
                    "baseline = frame 48",
                    "baseline = frame 1",
                 ]

APTS_dict = {
                "10" : "AF10P\_W22B24",
                "15" : "AF15P\_W22B3",
                "20" : "AF20P\_W22B6",
                "25" : "AF25P\_W22B7",
            }


pixel_pitch = re.findall(r'\d+', list_of_files[0])[0]

n_pixels = 16
make_diff = False
if len(list_of_files) == 2:
    make_diff = True
    fake_hit_rate_list_first = []

fig, ax1 = plt.subplots(figsize=(11,5))
plt.subplots_adjust(left=0.07,right=0.75,top=0.95)
err_bar_list = []
for file,label in zip(list_of_files, list_of_labels):

    tfile = ROOT.TFile(directory+file,"read")
    hist = tfile.Get("EventLoaderEUDAQ2/APTS_4/hPixelRawValues")
    list_of_thr = [10,20,30,40,50,60,70,80,90,100,110,120,130,140,150,160,170,180,190,200]

    thrs_list = []
    bins_list = []
    for thr in list_of_thr:
        for k in range(1, hist.GetNbinsX()):
            if hist.GetBinLowEdge(k) > thr:
                bins_list.append(k)
                thrs_list.append(hist.GetBinLowEdge(k))
                break

    n_events = (hist.GetEntries()-hist.GetBinContent(0))/n_pixels
    fake_hit_rate_list = []
    clusters_list = []

    for bin_min in bins_list:
        clusters = get_entries_in_range(hist, bin_min, hist.GetNbinsX()+1)
        clusters_list.append(clusters)
        fake_hit_rate_list.append(clusters/n_pixels/n_events)
        if make_diff and label == list_of_labels[0]:
            fake_hit_rate_list_first.append(clusters/n_pixels/n_events)


    ax1.errorbar(list_of_thr, fake_hit_rate_list, label=label, marker="s", linestyle='')

ax1.set_ylabel('Fake hit rate')
ax1.set_xlabel('threshold (ADCu)')
ax1.set_title('Vmin in the frames [49,55]')
#ax1.legend()

ax1.grid(axis='both')
ax1.set_yscale("log")

ax1.legend(loc='lower right',bbox_to_anchor =(1.32, -0.02),prop={"size":9})

x = 0.8
y = 0.99

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
        '$\\bf{%s}$'%APTS_dict[pixel_pitch],
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

plt.show()
fig.savefig('FakeHitRateVsThreshold.png', dpi=800)
if make_diff:
    fig, ax1 = plt.subplots(figsize=(11,5))
    plt.subplots_adjust(left=0.07,right=0.75,top=0.95)
    delta_fake_hit_rate = []
    for v1,v2 in zip(fake_hit_rate_list,fake_hit_rate_list_first):
        delta_fake_hit_rate.append(v1-v2)
    ax1.errorbar(list_of_thr, delta_fake_hit_rate, marker="s", linestyle='')

    ax1.set_ylabel('FHR(baseline = frame 1) - FHR(baseline = frame 48)')
    ax1.set_xlabel('threshold (ADCu)')
    ax1.set_title('Vmin in the frames [49,55]')
    ax1.legend()
    ax1.grid()

    ax1.legend(loc='lower right',bbox_to_anchor =(1.32, -0.02),prop={"size":9})

    x = 0.8
    y = 0.99

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
            '$\\bf{%s}$'%APTS_dict[pixel_pitch],
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

    plt.show()
    fig.savefig('DeltaFakeHitRateVsThreshold.png', dpi=800)

