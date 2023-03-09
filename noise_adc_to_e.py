from ROOT import TFile, TF1, TMath, TH1D, TCanvas
import matplotlib as mpl
import matplotlib.pyplot as plt
import math
import argparse
import yaml
import os
import re

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

    "AF25B_W22_1.2V":	    79.19905893,
    "AF25B_W22_0V":			43.49487644,
    "AF25B_W22_2.4V":		104.9121782,
    "AF25B_W22_3.6V":		118.5515334,
    "AF25B_W22_4.8V":		125.7991292,
    "AF10B_W22_1.2V":	    78.24761423,
    "AF10B_W22_0V":			42.92999417,
    "AF10B_W22_2.4V":		103.0991327,
    "AF10B_W22_3.6V":		115.96225,
    "AF10B_W22_4.8V":		122.5137794,
    "AF15P_W22_1.2V":	    79.84663062,
    "AF10P_W22_1.2V":		80.31095738,
    "AF10P_W22_0V":			45.23827032,
    "AF10P_W22_2.4V":		104.6569318,
    "AF10P_W22_3.6V":		117.084588,
    "AF10P_W22_4.8V":		122.9757817,
    "AF20P_W22_1.2V":       80.09704306,
    "AF25P_W22_1.2V":	    79.86636469,
    "AF25P_W22_0V":			44.43762416,
    "AF25P_W22_2.4V":		105.157962,
    "AF25P_W22_3.6V":		118.0621447,
    "AF25P_W22_4.8V":		124.3887409
}

parser = argparse.ArgumentParser()
parser.add_argument("config", help="Path to the YAML configuration file")
args = parser.parse_args()

with open(os.path.expandvars(args.config), 'r') as stream:
    try:
        params = yaml.full_load(stream)
    except yaml.YAMLError as exc:
        print(exc)
        
FILE_SUFFIX = params['FILE_SUFFIX']
NOISE_PATHS = params['NOISE_PATHS']
CHIPS = params['CHIPS']

plots_dir = "plots/"+FILE_SUFFIX
if not os.path.isdir(plots_dir):
    os.mkdir(plots_dir)

output = TFile(plots_dir+"/scaled_noise.root","recreate")
cv = TCanvas("cv","cv",1600,1200)

for noise_path, chip in zip(NOISE_PATHS, CHIPS):
    noise_file = TFile(noise_path, "read")
    noise_values = noise_file.Get(
        "EventLoaderEUDAQ2/APTS_3/hPixelRawValues")
    
    nbins = noise_values.GetNbinsX()
    min_x = noise_values.GetXaxis().GetBinLowEdge(1)*100/hundredElectronToADCu[chip]
    max_x = noise_values.GetXaxis().GetBinUpEdge(nbins)*100/hundredElectronToADCu[chip]
    min_x_or = noise_values.GetXaxis().GetBinLowEdge(1)
    max_x_or = noise_values.GetXaxis().GetBinUpEdge(nbins)
    new_hist = TH1D("scaled_noise_"+chip,noise_values.GetTitle()+"; pixel value (e^{-});"+noise_values.GetYaxis().GetTitle(),nbins,min_x,max_x)
    for i in range(1,nbins+1):
        new_hist.SetBinContent(i,noise_values.GetBinContent(i))
        new_hist.SetBinError(i,noise_values.GetBinError(i))
    new_hist.GetXaxis().SetRangeUser(-150,150)
    new_hist.Write()
    new_hist.Draw()
    cv.SaveAs(plots_dir+"/scale_noise"+chip+".png")
    
    noise_file.Close()

output.Close()