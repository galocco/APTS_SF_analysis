from itertools import count
from re import X
import numpy as np
import matplotlib.pyplot as plt
import ROOT

def compare_cluster_size(list_of_paths, list_of_labels, plot_name = 'cluster_size_comparison.png'):
    fig, ax1 = plt.subplots(figsize=(11,5))
    plt.subplots_adjust(left=0.07,right=0.75,top=0.95)
    for path,label in zip(list_of_paths,list_of_labels):
        file = ROOT.TFile(path,"read")
        cluster_size = file.Get("ClusteringAnalog/APTS_4/clusterSize")
        counts = []
        bins = [cluster_size.GetBinLowEdge(1)]
        for bin in range(1, 18):
            counts.append(cluster_size.GetBinContent(bin))
            bins.append(cluster_size.GetBinLowEdge(bin+1))

        bins = np.array(bins).astype(float)
        counts = np.array(counts).astype(float)
        centroids = (bins[1:] + bins[:-1]) / 2

        ax1.hist(centroids, bins=len(counts), weights=counts, range=(min(bins), max(bins)), histtype='step', density=True, label=label)
    
    ax1.legend(loc='lower right',bbox_to_anchor =(1.27, -0.02),prop={"size":10})

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

    ax1.set_xlabel('Cluster size', fontsize = 15)
    ax1.set_ylabel('Normalized counts', fontsize = 15)
    ax1.set_xlim(0.5,16)
    ax1.grid(True)
    fig.savefig(plot_name, dpi=800)
    plt.show()


list_of_paths = [
                "/home/giacomo/its-corryvreckan-tools/output/run000010/alignment_000010_DUT_cut40.root",
                "/home/giacomo/its-corryvreckan-tools/output/run000015/alignment_000015_DUT_cut60.root",
                "/home/giacomo/its-corryvreckan-tools/output/run000020/alignment_000020_DUT_cut80.root",
                "/home/giacomo/its-corryvreckan-tools/output/run000025/alignment_000025_DUT_cut100.root"
                ]

list_of_labels = [
                  "pitch 10um",
                  "pitch 15um",
                  "pitch 20um",
                  "pitch 25um"
                  ]

compare_cluster_size(list_of_paths,list_of_labels)