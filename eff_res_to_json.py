from ROOT import TFile, TH1D, TEfficiency
import argparse
import yaml
import os
import re
import math
import json

def is_compatible(acc, tot, target, nsigma=1):
    
    h_pass = TH1D("h_pass",";;",1,0,1)
    h_total = TH1D("h_total",";;",1,0,1)
    h_pass.SetBinContent(1,acc)
    h_total.SetBinContent(1,tot)
    pEff = TEfficiency(h_pass,h_total)
    eff = pEff.GetEfficiency(1)
    if eff < target:
        eff += nsigma*pEff.GetEfficiencyErrorUp(1)
        if eff > target:
            return True
    else:
        eff -= nsigma*pEff.GetEfficiencyErrorLow(1)
        if eff < target:
            return True
    return False

def reach_target(acc, tot, target, nsigma=1):
    
    h_pass = TH1D("h_pass",";;",1,0,1)
    h_total = TH1D("h_total",";;",1,0,1)
    h_pass.SetBinContent(1,acc)
    h_total.SetBinContent(1,tot)
    pEff = TEfficiency(h_pass,h_total)
    eff = pEff.GetEfficiency(1) + nsigma*pEff.GetEfficiencyErrorUp(1)
    if eff > target:
        return True
    return False


parser = argparse.ArgumentParser()
parser.add_argument("config", help="Path to the YAML configuration file")
args = parser.parse_args()

with open(os.path.expandvars(args.config), 'r') as stream:
    try:
        params = yaml.full_load(stream)
    except yaml.YAMLError as exc:
        print(exc)

CHIPS = params['CHIPS']
FILE_PATHS = params['FILE_PATHS']
NOISE_PATHS = params['NOISE_PATHS']
NSIGMANOISE = params['NSIGMANOISE']
TRACKINGRESOLUTIONS = params['TRACKINGRESOLUTIONS']
LABELS = params['LABELS']
FILE_SUFFIX = params['FILE_SUFFIX']

print(FILE_SUFFIX)
if NSIGMANOISE == 0:
    NOISE_PATHS = [None] * len(FILE_PATHS)


for file_path_list, noise_path, chip, trk_res, label in zip(FILE_PATHS, NOISE_PATHS, CHIPS, TRACKINGRESOLUTIONS, LABELS):
    if "cluster" not in label:
        eff_list = []
        err_eff_up = []
        err_eff_low = []
        charge = []
        clustersize_list = []
        err_clustersize_list = []
        err_res = []
        res_bin = []
        res_clu = []
        err_res_bin = []
        err_res_clu = []
        eff_target = 0.99

        #get apts Id
        file = TFile(file_path_list[0], "READ")
        subdir = file.Get("AnalysisDUT")
        key_list = subdir.GetListOfKeys()
        dir_list = []
        for key in key_list:
            if key.GetClassName() == "TDirectoryFile":
                dir_list.append(key.GetName())
        apts = dir_list[0]
        noise_rms = 0
        if NSIGMANOISE > 0:
            noise_file = TFile(noise_path, "read")
            noise_values = noise_file.Get(
                "EventLoaderEUDAQ2/"+apts+"/hPixelRawValues")
            noise_rms = noise_values.GetStdDev()
            noise_file.Close()

        print(file_path_list[0])

        hist = file.Get("AnalysisDUT/"+apts+"/seedChargeAssociated")

        unAssociated = file.Get("AnalysisDUT/"+apts+"/hUnassociatedTracksGlobalPosition")
    
        target = (hist.GetEntries()+unAssociated.GetEntries())*eff_target
        if not reach_target(hist.GetEntries(), hist.GetEntries()+unAssociated.GetEntries(), eff_target, nsigma=1):
            thr_eff99 = "None"
            err_thr_eff99_up = "None"
            err_thr_eff99_low = "None"
        else:
            tot = hist.GetBinContent(hist.GetNbinsX()+1)
            tot_old = 0
            for bin in range(0,hist.GetNbinsX()+1):
                tot += hist.GetBinContent(hist.GetNbinsX()-bin)
                if tot > target:
                    if math.modf(tot_old -target) < math.modf(tot-target):
                        thr_eff99 = hist.GetNbinsX()-bin+1
                        tot = tot_old
                    else:
                        thr_eff99 = hist.GetNbinsX()-bin
                    break
                tot_old += hist.GetBinContent(hist.GetNbinsX()-bin+1)

            err_thr_eff99_up = 0
            acc = tot
            for i in range(1,10000-thr_eff99):
                acc += hist.GetBinContent(thr_eff99 + i)
                isComp = is_compatible(acc, hist.GetEntries(), eff_target, 1)
                if not isComp:
                    break
                err_thr_eff99_up = i
                
            err_thr_eff99_low = 0
            acc = tot
            for i in range(1,thr_eff99):
                acc -= hist.GetBinContent(thr_eff99 - i)
                isComp = is_compatible(acc, hist.GetEntries(), eff_target, 1)
                if not isComp:
                    break
                err_thr_eff99_low = i

            err_thr_eff99_up = int(round(math.sqrt(1+err_thr_eff99_up**2),0))
            err_thr_eff99_low = int(round(math.sqrt(1+err_thr_eff99_low**2),0))


        file.Close()


    for file_path in file_path_list:
        input_file = TFile(file_path, "read")

        residualsX = input_file.Get(
            "AnalysisDUT/"+apts+"/local_residuals/residualsX")
        residualsY = input_file.Get(
            "AnalysisDUT/"+apts+"/local_residuals/residualsY")
        clusterSize = input_file.Get(
            "AnalysisDUT/"+apts+"/clusterSizeAssociated")
        efficiency = input_file.Get(
            "AnalysisEfficiency/"+apts+"/eTotalEfficiency")

        thr = int(re.findall(r'\d+', file_path)[-1])
        if thr < NSIGMANOISE*noise_rms:
            continue
        if "cluster" in label:
            eff_list.append(100*efficiency.GetEfficiency(1))
            err_eff_up.append(100*efficiency.GetEfficiencyErrorUp(1))
            err_eff_low.append(100*efficiency.GetEfficiencyErrorLow(1))
            charge.append(thr)
            clustersize_list.append(clusterSize.GetMean())
            err_clustersize_list.append(clusterSize.GetMeanError())

        res_x = math.sqrt(residualsX.GetStdDev()**2-trk_res[0]**2)
        res_y = math.sqrt(residualsY.GetStdDev()**2-trk_res[1]**2)
        if "cluster" in label:
            res_clu.append((res_x+res_y)/2.)        
            err_res_clu.append(math.sqrt(residualsX.GetStdDevError()**2+residualsY.GetStdDevError()**2)/2.)
        else:
            res_bin.append((res_x+res_y)/2.)        
            err_res_bin.append(math.sqrt(residualsX.GetStdDevError()**2+residualsY.GetStdDevError()**2)/2.)
        

    if "cluster" in label:
        info_dict = {
            "chip": chip,
            "resolutions_binary": res_bin,
            "resolutions_cluster": res_clu,
            "err_resolutions_binary": err_res_bin,
            "err_resolutions_cluster": err_res_clu,
            "err_clustersize": err_clustersize_list,
            "clustersize": clustersize_list,
            "efficiency": eff_list,
            "err_eff_low": err_eff_low,
            "err_eff_up": err_eff_up,
            "thr_eff99" : thr_eff99,
            "err_thr_eff99_up" : err_thr_eff99_up,
            "err_thr_eff99_low" : err_thr_eff99_low,
            "threshold": charge
        }

        with open("data/"+chip+".json", "w") as fp:
            json.dump(info_dict,fp) 
