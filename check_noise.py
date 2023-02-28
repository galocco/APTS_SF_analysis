from ROOT import TFile, TF1, TMath, TCanvas
import ROOT
import matplotlib as mpl
import matplotlib.pyplot as plt
import math
import argparse
import yaml
import os
import re


parser = argparse.ArgumentParser()
parser.add_argument("config", help="Path to the YAML configuration file")
args = parser.parse_args()

with open(os.path.expandvars(args.config), 'r') as stream:
    try:
        params = yaml.full_load(stream)
    except yaml.YAMLError as exc:
        print(exc)


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


noise_info = TFile(plots_dir+"/noise_info.root", "recreate")
th1_ratio = ROOT.TH1D("th1_ratio",";row+4*col;#frac{RMS_{3.6V}}{RMS_{0V}}",16,0,16)
cv = TCanvas("cv","cv")
for noise_path, label, chip, color in zip(NOISE_PATHS, LABELS, CHIPS, COLORS):
    sub_dir = noise_info.mkdir(label)
    
    noise_file = TFile(noise_path, "read")
    
    if chip == "AF25P_W22_1.2V" or "June" in label:
        apts = "4"
    else:
        apts = "3"

    th2_mean = ROOT.TH2D("th2_mean",";;",4,-0.5,3.5,4,-0.5,3.5)
    th2_sigma = ROOT.TH2D("th2_sigma",";;",4,-0.5,3.5,4,-0.5,3.5)
    th1_mean = ROOT.TH1D("th1_mean",";row+4*col;mean",16,0,16)
    th1_sigma = ROOT.TH1D("th1_sigma",";row+4*col;Std.Dev. (e^{-})",16,0,16)
    for i in range(4):
        for j in range(4):
            noise_values = noise_file.Get("EventLoaderEUDAQ2/APTS_"+apts+"/hPixelRawValuesPixel{}{}".format(i,j))
            print("EventLoaderEUDAQ2/APTS_"+apts+"/hPixelRawValues{}{}".format(i,j))
            noise_values.Write()
            sub_dir.cd()
            print(noise_values.GetMean()*100/hundredElectronToADCu[chip])
            th2_mean.SetBinContent(i+1,j+1,noise_values.GetMean()*100/hundredElectronToADCu[chip])
            th2_mean.SetBinError(i+1,j+1,noise_values.GetMeanError()*100/hundredElectronToADCu[chip])
            th2_sigma.SetBinContent(i+1,j+1,noise_values.GetStdDev()*100/hundredElectronToADCu[chip])
            th2_sigma.SetBinError(i+1,j+1,noise_values.GetStdDevError()*100/hundredElectronToADCu[chip])

            th1_mean.SetBinContent(1+i+j*4,noise_values.GetMean()*100/hundredElectronToADCu[chip])
            th1_mean.SetBinError(1+i+j*4,noise_values.GetMeanError()*100/hundredElectronToADCu[chip])
            th1_sigma.SetBinContent(1+i+j*4,noise_values.GetStdDev()*100/hundredElectronToADCu[chip])
            th1_sigma.SetBinError(1+i+j*4,noise_values.GetStdDevError()*100/hundredElectronToADCu[chip])
            cv.cd()
            noise_values.Draw("same")
            if "0V" in chip:
                th1_ratio.SetBinContent(1+i+j*4,noise_values.GetStdDev()*100/hundredElectronToADCu[chip])
                th1_ratio.SetBinError(1+i+j*4,noise_values.GetStdDevError()*100/hundredElectronToADCu[chip])
            if "2.4V" in chip:
                content = th1_ratio.GetBinContent(1+i+j*4)
                pre_error = th1_ratio.GetBinError(1+i+j*4)
                ratio = noise_values.GetStdDev()*100/hundredElectronToADCu[chip]/content
                error = ratio*TMath.Sqrt((noise_values.GetStdDevError()/noise_values.GetStdDev())**2+(pre_error/content)**2)
                th1_ratio.SetBinContent(1+i+j*4,ratio)
                th1_ratio.SetBinError(1+i+j*4,error)
                
    sub_dir.cd()
    th1_mean.Fit('pol0')
    th1_sigma.Fit('pol0')
    th2_mean.Write()
    th2_sigma.Write()
    th1_mean.Write()
    th1_sigma.Write()
noise_info.cd()
cv.Write()
th1_ratio.Fit('pol0')
th1_ratio.Write()
noise_info.Close()
