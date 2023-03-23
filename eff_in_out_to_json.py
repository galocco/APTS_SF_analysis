from ROOT import TFile, TH2D, TEfficiency
import argparse
import yaml
import os
import re
import json


def mergeTH2D(hist, border):
    new_hist = TH2D(hist.GetName()+"_new","",3,0,3,3,0,3)
    edge = 0
    pitch = hist.GetNbinsY()*hist.GetXaxis().GetBinWidth(1)
    for i in range(1,hist.GetNbinsX()+1):
        posx = i*hist.GetXaxis().GetBinWidth(1)
        for j in range(1,hist.GetNbinsY()+1):
            posy = j*hist.GetYaxis().GetBinWidth(1)
            if posy<border or posy>pitch-border or posx<border or posx>pitch-border:
                edge += hist.GetBinContent(i, j)

    for i in range(1,4):
        for j in range(1,4):
            new_hist.SetBinContent(i,j,edge)
    center = hist.GetEntries()
    new_hist.SetBinContent(2,2, center-edge)
    return new_hist

parser = argparse.ArgumentParser()
parser.add_argument('-e', '--edge',
                    help='Border width in um', type=float, default=2.1)
parser.add_argument("config", help="Path to the YAML configuration file")
args = parser.parse_args()
square_edge = args.edge

with open(os.path.expandvars(args.config), 'r') as stream:
    try:
        params = yaml.full_load(stream)
    except yaml.YAMLError as exc:
        print(exc)

CHIPS = params['CHIPS']
FILE_PATHS = params['FILE_PATHS']
NOISE_PATHS = params['NOISE_PATHS']
NSIGMANOISE = params['NSIGMANOISE']
EFF_RANGE = params['EFF_RANGE']
pitch_list =[]
for file_path_list, noise_path, chip in zip(FILE_PATHS, NOISE_PATHS, CHIPS):
    
    
    eff_cent_list = []
    err_eff_cent_up = []
    err_eff_cent_low = []

    eff_edge_list = []
    err_eff_edge_up = []
    err_eff_edge_low = []
    charge_cent = []
    charge_edge = []

    root_file = TFile(file_path_list[0], "READ")
    subdir = root_file.Get("AnalysisDUT")
    key_list = subdir.GetListOfKeys()
    dir_list = []
    for key in key_list:
        if key.GetClassName() == "TDirectoryFile":
            dir_list.append(key.GetName())
    apts = dir_list[0]
    root_file.Close()

    noise_file = TFile(noise_path, "read")
    noise_values = noise_file.Get("EventLoaderEUDAQ2/"+apts+"/hPixelRawValues")
    noise_rms = noise_values.GetStdDev()
    noise_file.Close()

    for file_path in file_path_list:
        thr = int(re.findall(r'\d+', file_path)[-1])
        if thr < noise_rms*NSIGMANOISE:
            continue
        input_file = TFile(file_path, "read")

        efficiency = input_file.Get("AnalysisEfficiency/"+apts+"/pixelEfficiencyMap_trackPos")
        passed = efficiency.GetPassedHistogram()
        total = efficiency.GetTotalHistogram()

        passed = mergeTH2D(passed, square_edge)
        total = mergeTH2D(total, square_edge)

        efficiency = TEfficiency(passed,total)
        if 100*efficiency.GetEfficiency(12) > EFF_RANGE[0]:
            eff_cent_list.append(100*efficiency.GetEfficiency(12))
            err_eff_cent_up.append(100*efficiency.GetEfficiencyErrorUp(12))
            err_eff_cent_low.append(100*efficiency.GetEfficiencyErrorLow(12))
            charge_cent.append(thr)

        if 100*efficiency.GetEfficiency(11) > EFF_RANGE[0]:
            eff_edge_list.append(100*efficiency.GetEfficiency(11))
            err_eff_edge_up.append(100*efficiency.GetEfficiencyErrorUp(11))
            err_eff_edge_low.append(100*efficiency.GetEfficiencyErrorLow(11))
            charge_edge.append(thr)
    
    info_dict = {
        "chip": chip,
        "noise_rms": noise_rms,
        "efficiency_center": eff_cent_list,
        "err_eff_center_low": err_eff_cent_low,
        "err_eff_center_up": err_eff_cent_up,
        "efficiency_edge": eff_edge_list,
        "err_eff_edge_low": err_eff_edge_low,
        "err_eff_edge_up": err_eff_edge_up,
        "threshold_edge": charge_edge,
        "threshold_center": charge_cent,
    }

    with open("data/"+chip+"_inpixel_sel.json", "w") as fp:
        json.dump(info_dict,fp) 
