from itertools import count
from re import X
import numpy as np
import matplotlib.pyplot as plt
import ROOT

def compare_cluster_size(list_of_paths, list_of_labels, plot_name = 'cluster_size_comparison.png'):
    fig, ax = plt.subplots(figsize=(8, 5))
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

        counts_, bins_, _ = plt.hist(centroids, bins=len(counts), weights=counts, range=(min(bins), max(bins)), histtype='step', density=True, label=label)

    plt.xlabel('Cluster size', fontsize = 15)
    plt.ylabel('Normalized counts', fontsize = 15)
    plt.xlim(0.5,16)
    plt.grid(True)
    plt.legend(prop={'size': 10})
    plt.savefig(plot_name, dpi=800)
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