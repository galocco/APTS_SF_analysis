import ROOT

path_good = "/home/giacomo/APTS_SF_analysis/good.root"
path_bad = "/home/giacomo/APTS_SF_analysis/bad.root"

path_list = [
                "/home/giacomo/APTS_SF_analysis/bad.root",
                "/home/giacomo/APTS_SF_analysis/good.root",
                "/home/giacomo/APTS_SF_analysis/24.root",
                "/home/giacomo/APTS_SF_analysis/36.root",
                "/home/giacomo/APTS_SF_analysis/48.root"
            ]

label_list = ["0V","1.2V","2.4V","3.6V","4.8V"]

fileGood = ROOT.TFile(path_good,"read")


for path,label in zip(path_list,label_list):
    file = ROOT.TFile(path,"read")
    rate = 0
    cluster = 0
    histTrack = file.Get("Tracking4D/hasTracksVsEvent")
    histCluster = file.Get("ClusteringAnalog/APTS_3/hasTracksVsEvent")

    for bin in range(1, histCluster.GetNbinsX()):
        
        hasCluster = histCluster.GetBinContent(bin)
        hasTracks   = histTrack.GetBinContent(bin+1)

        if hasCluster == 1:
            cluster += 1 
            if hasCluster == hasTracks:
                rate += 1

    rate /= cluster

    print(label+": coincidence rate = ", round(rate,2), ", number of clusters = ",cluster)