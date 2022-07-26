from distutils.archive_util import make_archive
import ROOT
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np

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

n_pixels = 16
make_diff = False
if len(list_of_files) == 2:
    make_diff = True
    fake_hit_rate_list_first = []

plt.figure(figsize=(8,5))

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


    plt.errorbar(list_of_thr, fake_hit_rate_list, label=label, marker="s", linestyle='')

plt.ylabel('Fake hit rate')
plt.xlabel('threshold (ADCu)')
plt.title('Vmin in the frames [49,55]')
plt.legend()
plt.grid()
plt.yscale("log")
plt.savefig('FakeHitRateVsThreshold.png', dpi=800)
plt.show()

if make_diff:
    plt.figure(figsize=(8,5))
    delta_fake_hit_rate = []
    for v1,v2 in zip(fake_hit_rate_list,fake_hit_rate_list_first):
        delta_fake_hit_rate.append(v1-v2)
    plt.errorbar(list_of_thr, delta_fake_hit_rate, marker="s", linestyle='')

    plt.ylabel('FHR(baseline = frame 1) - FHR(baseline = frame 48)')
    plt.xlabel('threshold (ADCu)')
    plt.title('Vmin in the frames [49,55] ')
    plt.legend()
    plt.grid()
    plt.savefig('DeltaFakeHitRateVsThreshold.png', dpi=800)
    plt.show()

