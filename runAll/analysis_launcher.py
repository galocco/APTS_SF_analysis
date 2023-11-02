#based on chatGPTs
import subprocess
import argparse
import os
import os.path
import re
import csv
import utils
from ROOT import TFile, TF1
import yaml
import copy
import shutil

run_numbers =    [
                    #3061414322307291414
]
"""
    212130609230523141229, #2023-05_SPS-3REF-2APTSSF-3REF-B1-AF10P_W22B24.conf,AF10P_W22B24,4.8,1,None
    212130608230523130623, #2023-05_SPS-3REF-2APTSSF-3REF-B1-AF10P_W22B24.conf,AF10P_W22B24,0.0,1,None
    212130610230523145053, #2023-05_SPS-3REF-2APTSSF-3REF-B1-AF10P_W22B24.conf,AF10P_W22B24,1.2,1,None
    212130611230523153328, #2023-05_SPS-3REF-2APTSSF-3REF-B1-AF10P_W22B24.conf,AF10P_W22B24,1.2,1,None
    212130612230523164632, #2023-05_SPS-3REF-2APTSSF-3REF-B1-AF10P_W22B24.conf,AF10P_W22B24,1.2,1,None
    212130613230523173340, #2023-05_SPS-3REF-2APTSSF-3REF-B1-AF10P_W22B24.conf,AF10P_W22B24,1.2,1,None
    212130614230523181235, #2023-05_SPS-3REF-2APTSSF-3REF-B1-AF10P_W22B24.conf,AF10P_W22B24,1.2,1,None
    212130615230523191912, #2023-05_SPS-3REF-2APTSSF-3REF-B1-AF10P_W22B24.conf,AF10P_W22B24,1.2,1,None
    207164410230521205957, #2023-05_SPS-3REF-2APTSSF-3REF-B1-AF10P_W22B59.conf,AF10P_W22B59,4.8,1,1.00E+15
    207164411230521212557, #2023-05_SPS-3REF-2APTSSF-3REF-B1-AF10P_W22B59.conf,AF10P_W22B59,4.8,1,1.00E+15
    207164404230521164418, #2023-05_SPS-3REF-2APTSSF-3REF-B1-AF10P_W22B59.conf,AF10P_W22B59,0.0,1,1.00E+15
    207164405230521172553, #2023-05_SPS-3REF-2APTSSF-3REF-B1-AF10P_W22B59.conf,AF10P_W22B59,1.2,1,1.00E+15
    207164406230521180318, #2023-05_SPS-3REF-2APTSSF-3REF-B1-AF10P_W22B59.conf,AF10P_W22B59,0.0,1,1.00E+15
    207164407230521203000, #2023-05_SPS-3REF-2APTSSF-3REF-B1-AF10P_W22B59.conf,AF10P_W22B59,1.2,1,1.00E+15
"""
#list of runs

#list of thresholds in electrons
seed_thresholds_in_e =  [0,20,40,60,70,80,90,100,120,140,160,180,200,250,300]
#list of the threshold in ADCu if you want to use yours
#add an item with the Vbb and the list 
#AF15P_W22_0.0V_1.00E+13
seed_thresholds = {
                    "AF20P_W22_1.2V" : [145, 161, 201],
                    "AF25P_W22_1.2V" : [169],
                    "AF25P_W22_1.2V_1.00E+13" : [166],
                    "AF25P_W22_1.2V_1.00E+14" : [130],
                    "AF20P_W22_1.2V_1.00E+13" : [156],
                    "AF20P_W22_1.2V_1.00E+14" : [156],
                    "AF15P_W22_1.2V_1.00E+13" : [134],
                    "AF15P_W22_1.2V_1.00E+14" : [125],
                    "AF10P_W22_1.2V_1.00E+15" : [95],
                    "AF10P_W22_4.8V_1.00E+15" : [136],
                    "AF10P_W22_1.2V" : [128],
                    "AF25B_W22_1.2V" : [115],
                    "AF10B_W22_1.2V" : [130],
                    "AF10P_W22_4.8V_2.00E+15" : [104]
                }
#polynomial grade for the eta correction. 5 is fine
poly_grades = [3]
#list clustering methods
#same names as in ClusteringAnalog. Only cluster_eta is different, use it to run the analysis with cluster + eta correction
methods = ["binary"]#,"cluster_eta"]#"window","binary","cluster"]

parser = argparse.ArgumentParser()
parser.add_argument(
    '-al', '--alignment', help='Run the alignment', action='store_true')
parser.add_argument(
    '-an', '--analysis', help='Run the analysis', action='store_true')
parser.add_argument(
    '-e', '--eta', help='Run the eta correction', action='store_true')
parser.add_argument(
    '-t', '--thr', help='Use fixed ADCu thresholds', action='store_true')
parser.add_argument(
    '-r', '--recy', help='Recycle geometry file', action='store_true')
parser.add_argument(
    '-m', '--merge', help='Merge eta corrections', action='store_true')
parser.add_argument(
    '-ps', '--ps', help='Merge eta corrections', action='store_true')
parser.add_argument(
    '-u', '--usemerged', help='Use merged eta corrections', action='store_true')
parser.add_argument(
    '-a', '--mami', help='MAMI', action='store_true')
parser.add_argument(
    '-o', '--october', help='Use merged eta corrections', action='store_true')
parser.add_argument(
    '-j', '--june', help='Use merged eta corrections', action='store_true')
parser.add_argument(
    '-mux', '--mux', help='Study mux data', action='store_true')
parser.add_argument(
    '-a1', '--august_b1', help='Use merged eta corrections', action='store_true')
parser.add_argument(
    '-a2', '--august_b2', help='Use merged eta corrections', action='store_true')
parser.add_argument(
    '-e9', '--eff99', help='Use merged eta corrections', action='store_true')
#parser.add_argument("config", help="Path to the YAML configuration file")
args = parser.parse_args()

#with open(os.path.expandvars(args.config), 'r') as stream:
#    try:
#        params = yaml.full_load(stream)
#    except yaml.YAMLError as exc:
#        print(exc)
#run_numbers = params["RUN_NUMBERS"]
RUN_ALIGNMENT = args.alignment
RUN_ANALYSIS = args.analysis
RUN_ETA = args.eta
ADCU_THR = args.thr
RECYCLE = args.recy
MERGE_ETA = args.merge
USE_MERGED_ETA = args.usemerged 
OCTOBER = args.october
JUNE = args.june
AUGUST_B1 = args.august_b1
AUGUST_B2 = args.august_b2
MAMI = args.mami
MUX = args.mux
PS = args.ps
ADD_THR_EFF99 = args.eff99
#csv file with the run list
csv_file = "data/runsSPSMay23.csv"
#directory with the data
data_dir = "data/2023-05_SPS"
#directory with the configs files
config_dir = "configs/2023-05_SPS"
#directory for the output
output_dir = "2023-05_SPS" #no need for output
if OCTOBER:
    csv_file = "data/runsSPSOctober22.csv"
    #directory with the data
    data_dir = "data/2022-10_SPS"
    #directory with the configs files
    config_dir = "configs/2022-10_SPS"
    #directory for the output
    output_dir = "2022-10_SPS" #no need for output

    run_numbers = [
                        413221453221013042711
                    ]

if JUNE:
    csv_file = "data/runsPSJune22.csv"
    #directory with the data
    data_dir = "data/2022-06_PS"
    #directory with the configs filesrunsPSAugust22_B2.csv
    config_dir = "configs/2022-06_PS"
    #directory for the output
    output_dir = "2022-06_PS" #no need for output
    run_numbers = [
                        #253195220220622195234, #2022-06_PS-2REF-APTSSF-DPTS-2REF.conf-AF25P_W22B7.conf,AF25P_W22B7,1.2,1
                        255161234220624161249, #2022-06_PS-2REF-APTSSF-DPTS-2REF-AF15P_W22B3.conf,AF15P_W22B3,1.2,1,None
                        256073154220625073209#, #2022-06_PS-2REF-APTSSF-DPTS-2REF-AF15P_W22B3.conf,AF15P_W22B3,1.2,1,None
                    ]
if PS:
    csv_file = "data/runsPSMay23.csv"
    #directory with the data
    data_dir = "data/2023-05_PS"
    #directory with the configs filesrunsPSAugust22_B2.csv
    config_dir = "configs/2023-05_PS"
    #directory for the output
    output_dir = "2023-05_PS" #no need for output
    run_numbers = [
                        #191211908230509051130,#15
                        183220839230504034940,#20
                        #192125512230509125517#25
                    ]
if MAMI:
    csv_file = "data/runsMAMIApril22.csv"
    #directory with the data
    data_dir = "data/2022-04_MAMI"
    #directory with the configs filesrunsPSAugust22_B2.csv
    config_dir = "configs/2022-04_MAMI"
    #directory for the output
    output_dir = "2022-04_MAMI" #no need for output
    run_numbers = [
                        152042027220412043047,
                    ]
if MUX:
    csv_file = "data/runsSPSJuly23.csv"
    #directory with the data
    data_dir = "data/2023-07_SPS"
    #directory with the configs filesrunsPSAugust22_B2.csv
    config_dir = "configs/2023-07_SPS"
    #directory for the output
    output_dir = "2023-07_SPS" #no need for output
    run_numbers = [
                    306224759230730080014,
                    #306224747230730040908, #2023-07_SPS-3REF-2APTSSF-3REF-AF10PM_W22B4.conf,AF10PM_W22B4,0.0,1,None,0
                    #306141432230729141446,
                    #306224721230729224735, #2023-07_SPS-3REF-2APTSSF-3REF-AF10PM_W22B4.conf,AF10PM_W22B4,0.0,1,None,0
                    #306224723230729231120, #2023-07_SPS-3REF-2APTSSF-3REF-AF10PM_W22B4.conf,AF10PM_W22B4,0.0,1,None,0
                    #306224725230729233502, #2023-07_SPS-3REF-2APTSSF-3REF-AF10PM_W22B4.conf,AF10PM_W22B4,0.0,1,None,0
                    #306224727230730000031, #2023-07_SPS-3REF-2APTSSF-3REF-AF10PM_W22B4.conf,AF10PM_W22B4,0.0,1,None,0
                    #306224729230730002444, #2023-07_SPS-3REF-2APTSSF-3REF-AF10PM_W22B4.conf,AF10PM_W22B4,0.0,1,None,0
                    #306224731230730004926, #2023-07_SPS-3REF-2APTSSF-3REF-AF10PM_W22B4.conf,AF10PM_W22B4,0.0,1,None,0
                    #306224733230730011312, #2023-07_SPS-3REF-2APTSSF-3REF-AF10PM_W22B4.conf,AF10PM_W22B4,0.0,1,None,0
                    #306224735230730013729, #2023-07_SPS-3REF-2APTSSF-3REF-AF10PM_W22B4.conf,AF10PM_W22B4,0.0,1,None,0
                    #306224737230730020856, #2023-07_SPS-3REF-2APTSSF-3REF-AF10PM_W22B4.conf,AF10PM_W22B4,0.0,1,None,0
                    #306224739230730023252, #2023-07_SPS-3REF-2APTSSF-3REF-AF10PM_W22B4.conf,AF10PM_W22B4,0.0,1,None,0
                    #306224741230730025709, #2023-07_SPS-3REF-2APTSSF-3REF-AF10PM_W22B4.conf,AF10PM_W22B4,0.0,1,None,0
                    #306224743230730032109, #2023-07_SPS-3REF-2APTSSF-3REF-AF10PM_W22B4.conf,AF10PM_W22B4,0.0,1,None,0
                    #306224745230730034453, #2023-07_SPS-3REF-2APTSSF-3REF-AF10PM_W22B4.conf,AF10PM_W22B4,0.0,1,None,0
                    #306224749230730060128, #2023-07_SPS-3REF-2APTSSF-3REF-AF10PM_W22B4.conf,AF10PM_W22B4,0.0,1,None,0
                    #306224751230730062512, #2023-07_SPS-3REF-2APTSSF-3REF-AF10PM_W22B4.conf,AF10PM_W22B4,0.0,1,None,0
                    #306224753230730064910, #2023-07_SPS-3REF-2APTSSF-3REF-AF10PM_W22B4.conf,AF10PM_W22B4,0.0,1,None,0
                    #306224755230730071244, #2023-07_SPS-3REF-2APTSSF-3REF-AF10PM_W22B4.conf,AF10PM_W22B4,0.0,1,None,0
                    #306224757230730073628, #2023-07_SPS-3REF-2APTSSF-3REF-AF10PM_W22B4.conf,AF10PM_W22B4,0.0,1,None,0
                    #306224759230730080014, #2023-07_SPS-3REF-2APTSSF-3REF-AF10PM_W22B4.conf,AF10PM_W22B4,0.0,1,None,0
                    #306224761230730082736, #2023-07_SPS-3REF-2APTSSF-3REF-AF10PM_W22B4.conf,AF10PM_W22B4,0.0,1,None,0
                    #307090059230730091310, #2023-07_SPS-3REF-2APTSSF-3REF-AF10PM_W22B4.conf,AF10PM_W22B4,0.0,1,None,0
                    #307090061230730093700, #2023-07_SPS-3REF-2APTSSF-3REF-AF10PM_W22B4.conf,AF10PM_W22B4,0.0,1,None,0
                    ]
if AUGUST_B1:
    csv_file = "data/runsPSAugust22_B1.csv"
    #directory with the data
    data_dir = "data/2022-08_PS"
    #directory with the configs files
    config_dir = "configs/2022-08_PS_B1"
    #directory for the output
    output_dir = "2022-08_PS" #no need for output
    run_numbers =    [
                        #344201631220825201636, #2022-08_PS-3REF-2APTSSF-2REF-B1-AF10P_W22B28.conf,AF10P_W22B28,1.2,1
                        #347092422220828092436, #2022-08_PS-3REF-2APTSSF-2REF-B1-AF15P_W22B2.conf,AF15P_W22B2,1.2,1
                        #346123556220827123602, #2022-08_PS-3REF-2APTSSF-2REF-B1-AF15P_W22B2.conf,AF15P_W22B2,4.8,1
                        #346175802220827175808, #2022-08_PS-3REF-2APTSSF-2REF-B1-AF15P_W22B2.conf,AF15P_W22B2,4.8,1
                        346175803220827193601, #2022-08_PS-3REF-2APTSSF-2REF-B1-AF15P_W22B2.conf,AF15P_W22B2,0.0,1
                        #347150143220828150148, #2022-08_PS-3REF-2APTSSF-2REF-B1-AF15P_W22B2.conf,AF15P_W22B2,2.4,1
                        #347200432220828200437, #2022-08_PS-3REF-2APTSSF-2REF-B1-AF15P_W22B2.conf,AF15P_W22B2,3.6,1
                    ]


if AUGUST_B2:
    csv_file = "data/runsPSAugust22_B2.csv"
    #directory with the data
    data_dir = "data/2022-08_PS"
    #directory with the configs files
    config_dir = "configs/2022-08_PS_B2"
    #directory for the output
    output_dir = "2022-08_PS" #no need for output

    run_numbers = [
                        345171002220826171008, #2022-08_PS-3REF-2APTSSF-3REF-B2-AF20P_W22B6.conf,AF20P_W22B6,1.2,1
                        345211441220826211447, #2022-08_PS-3REF-2APTSSF-3REF-B2-AF20P_W22B6.conf,AF20P_W22B6,1.2,1
                        345211442220826233620, #2022-08_PS-3REF-2APTSSF-3REF-B2-AF20P_W22B6.conf,AF20P_W22B6,0.0,1
                        345211450220827042644, #2022-08_PS-3REF-2APTSSF-3REF-B2-AF20P_W22B6.conf,AF20P_W22B6,4.8,1
                    ]

def move_outputs():
    # Check if the directory exists
    if not os.path.exists("log_files"):
        # If it doesn't exist, create it
        os.makedirs("log_files")

    # Check if the directory exists
    if not os.path.exists("conf_files"):
        # If it doesn't exist, create it
        os.makedirs("conf_files")

        # Source and destination directories
    source_dir = "."
    destination_dir = "conf_files"
    # List files in the source directory
    files = os.listdir(source_dir)

    for file in files:
        if file.endswith(".conf"):
            source_file = os.path.join(source_dir, file)
            destination_file = os.path.join(destination_dir, file)

            # Move the file to the destination directory
            shutil.move(source_file, destination_file)
    
    source_dir = "."
    destination_dir = "log_files"
    # List files in the source directory
    files = os.listdir(source_dir)

    for file in files:
        if file.endswith(".log"):
            source_file = os.path.join(source_dir, file)
            destination_file = os.path.join(destination_dir, file)

            # Move the file to the destination directory
            shutil.move(source_file, destination_file)


    

def apply_eta_contants(log_file, config_file, grade = 5, output_dir = "SPSOctober22/B1"):
    '''
    '''
    eta_correction = ""
    with open(log_file) as f:
        while True:
            line = f.readline()
            if not line:
                break
            if line.strip()=="[EtaCorrection]":
                eta_correction += line.strip() + "\n"
                line = f.readline()
                eta_correction += line.strip() + "\n"
                line = f.readline()
                eta_correction += line.strip() + "\n"
                line = f.readline()
                eta_correction += line.strip() + "\n"
                line = f.readline()
                eta_correction += line.strip() + "\n"
                line = f.readline()
                eta_correction += line.strip() + "\n"
                break
    
    # Open the file in read mode and read all its lines into a list
    with open(config_file, 'r') as file:
        lines = file.readlines()
    print(lines[6])
    lines[6] = f'histogram_file = "{output_dir}/@DUT@/analysis_@RunNumber@_@Method@_eta{grade}_@ThresholdNeigh@_@ThresholdSeed@.root"\n'
    lines.insert(7, "")
    lines.insert(40, eta_correction)

    # Open the file in write mode and write the modified list to the file
    with open(config_file, 'w') as file:
        file.writelines(lines)

def set_pol_grade(config_file, grade, odd=False, output_dir = "SPSOctober22/B1"):
    if grade < 0:
        print("ERROR: grade < 0 -> grade set to 0")
        grade = 0

    eta_formula_x = 'eta_formula_x = "[0]'
    eta_formula_y = 'eta_formula_y = "[0]'
    if odd:
        eta_formula_x = 'eta_formula_x = "'
        eta_formula_y = 'eta_formula_y = "'
    power = 0
    parameter = 0
    while grade != power:
        power += 1
        if odd and power%2==0:
            continue
        parameter += 1

        if power == 1:
            if odd:
                eta_formula_x += f"[{parameter}]*x"
                eta_formula_y += f"[{parameter}]*x"
            else:
                eta_formula_x += f" + [{parameter}]*x"
                eta_formula_y += f" + [{parameter}]*x"
        else:
            eta_formula_x += f' + [{parameter}]*x^{power}'
            eta_formula_y += f' + [{parameter}]*x^{power}'
    

    # Open the file in read mode and read all its lines into a list
    with open(config_file, 'r') as file:
        lines = file.readlines()

    lines[6] = f'histogram_file         = "{output_dir}/@DUT@/analysis_eta{grade}_@RunNumber@_@ThresholdNeigh@_@ThresholdSeed@.root"\n'

    lines[62] = eta_formula_x +'"\n'
    lines[63] = eta_formula_y +'"\n'

    # Open the file in write mode and write the modified list to the file
    with open(config_file, 'w') as file:
        file.writelines(lines)

def get_chip(csv_file, run_number):
    # Open the CSV file for reading
    with open(csv_file, 'r') as file:
        # Create a CSV reader object
        csv_reader = csv.reader(file)
        for row in csv_reader:
            if row[0] == str(run_number):
                #return row[4]
                return row[2]
        
    return None

def get_Vbb(csv_file, run_number):
    # Open the CSV file for reading
    with open(csv_file, 'r') as file:
        # Create a CSV reader object
        csv_reader = csv.reader(file)
        for row in csv_reader:
            if row[0] == str(run_number):
                #return row[4]
                return row[3]
        
    return None

def get_Ireset(csv_file, run_number):
    # Open the CSV file for reading
    with open(csv_file, 'r') as file:
        # Create a CSV reader object
        csv_reader = csv.reader(file)
        for row in csv_reader:
            if row[0] == str(run_number):
                #return row[4]
                return row[4]
        
    return None
def get_Irrad(csv_file, run_number):
    # Open the CSV file for reading
    with open(csv_file, 'r') as file:
        # Create a CSV reader object
        csv_reader = csv.reader(file)
        for row in csv_reader:
            if row[0] == str(run_number):
                #return row[4]
                return row[5]
        
    return None

def get_status_chip(chip, vbb, irrad="None", ireset="1"):
    # Iterate over index
    new_chip = chip[0]
    for element in range(1, len(chip)):
        if chip[element] == "B" and (chip[element-1] != "5" and chip[element-1] != "0"):
            break
        new_chip += chip[element]
        
    status_chip = new_chip+"_"+vbb+"V"
    if irrad != "None":
        status_chip += "_"+irrad
    if ireset != "1":
        status_chip += "_IR"+ireset
    if status_chip not in utils.hundredElectronToADCu:
        print("ATTENTION: conversion factor not available!!!!!!! using the not irradiated ")
        status_chip = new_chip+"_"+vbb+"V"
    return status_chip

def get_nice_thresholds(threshold_list, path_noise, chip, vbb, irrad="None", ireset="1", reject_below_noise = True, nsigma_noise = 3):
    threshold_list_tmp = copy.copy(threshold_list)
    status_chip = get_status_chip(chip, vbb, irrad, ireset)
    root_file = TFile(path_noise, "READ")
    subdir = root_file.Get("EventLoaderEUDAQ2")
    key_list = subdir.GetListOfKeys()
    for key in key_list:
        if key.GetClassName() == "TDirectoryFile" and "APTS" in key.GetName():
            apts = key.GetName()
            break

    noise_values = root_file.Get(
        "EventLoaderEUDAQ2/"+apts+"/hPixelRawValues")
    print("plotting above ", noise_values.GetStdDev(), " ADCu")
    print("plotting above ", noise_values.GetStdDev()*nsigma_noise, " ADCu")

    eThrLimit = noise_values.GetStdDev()*nsigma_noise*100/utils.hundredElectronToADCu[status_chip]
    root_file.Close()
    rejected_list = []
    if reject_below_noise:
        for thr in threshold_list_tmp:
            #print(thr)
            if thr < eThrLimit:
                #print("rejected", thr)
                rejected_list.append(thr)
    for rej in rejected_list:
        threshold_list_tmp.remove(rej)
    threshold_list_tmp.insert(0, eThrLimit+1)
    
    return threshold_list_tmp

def convert_to_adc(thresholds,chip, vbb, irrad="None", ireset="1", round_thr = True):
    status_chip = get_status_chip(chip, vbb, irrad, ireset)

    thresholds_in_adc = []
    for thr in thresholds:
        new_thr = thr/100*utils.hundredElectronToADCu[status_chip]
        if round_thr:
            new_thr = round(new_thr, 0)
        thresholds_in_adc.append(int(new_thr))
    return thresholds_in_adc

def get_runnumber_aligned(run_number, csv_file):
    # Open the CSV file for reading
    with open(csv_file, 'r') as file:
        # Create a CSV reader object
        csv_reader = csv.reader(file)
        for row in csv_reader:
            if row[0] == str(run_number):
                #return row[4]
                ideal_geometry = row[1]
                break
                
    with open(csv_file, 'r') as file:
        # Create a CSV reader object
        csv_reader = csv.reader(file)
        for row in csv_reader:
            print(row)
            if row[1] == ideal_geometry:
                if os.path.isfile(f"geometry/aligned_{row[0]}_DUT_step4.conf"):
                    return row[0], True
    return None, False

def get_runnumber_etanoise(run_number, csv_file, chip, vbb, irrad, ireset, grade, threshold=True):

    status_chip = get_status_chip(chip, vbb, irrad, ireset)
    # Open the CSV file for reading
    with open(csv_file, 'r') as file:
        # Create a CSV reader object
        csv_reader = csv.reader(file)
        for row in csv_reader:
            if row[0] == str(run_number):

                #return row[4]
                ideal_geometry = row[1]
                break

    with open(csv_file, 'r') as file:

        csv_reader = csv.reader(file)
        #print(status_chip)
        #print(ideal_geometry)
        for row in csv_reader:
            #print(row[0])
            #print(row[1])
            #print(get_status_chip(row[2], row[3], row[5], row[4]))
            if row[1] == ideal_geometry and  get_status_chip(row[2], row[3], row[5], row[4])==status_chip:
                if not isinstance(threshold, list):
                    return row[0], True
                else:
                    for thr in threshold:
                        if not os.path.isfile(f"compute_eta_run_{row[0]}-dut:{chip}-thr{thr}_pol{grade}.log"):
                            return row[0], False
                    return row[0], True
    return None, False


def fit_merged_tprofile(path, formula_x, formula_y, file_name):
    tf1x = TF1("tf1x",formula_x)
    tf1y = TF1("tf1y",formula_y)

    root_file = TFile(path, "READ")
    subdir = root_file.Get("EventLoaderEUDAQ2")
    key_list = subdir.GetListOfKeys()
    for key in key_list:
        if key.GetClassName() == "TDirectoryFile" and "APTS" in key.GetName():
            apts = key.GetName()
            break

    eta_x = root_file.Get("EtaCalculation/"+apts+"/etaDistributionXprofile")
    eta_y = root_file.Get("EtaCalculation/"+apts+"/etaDistributionYprofile")

    output = TFile(file_name,"recreate")
    eta_x.Fit(tf1x,"M+")
    eta_y.Fit(tf1y,"M+")
    eta_x.Write()
    eta_y.Write()
    output.Close()

    pars_x = ""
    for i in range(0,tf1x.GetNumberFreeParameters()):
        pars_x += str(tf1x.GetParameter(i))+" "

    pars_y = ""
    for i in range(0,tf1y.GetNumberFreeParameters()):
        pars_y += str(tf1y.GetParameter(i))+" "

    return apts, pars_x, pars_y

def write_eta_correction(apts, file_path, formula_x, formula_y, pars_x, pars_y):
    txt = open(file_path, "w")
    txt.write("[EtaCorrection]\n")
    txt.write("name = "+apts+"\n")
    txt.write("eta_formula_x = \""+formula_x+"\"\n") 
    txt.write("eta_constants_x = "+pars_x+"\n")
    txt.write("eta_formula_y = \""+formula_y+"\"\n")
    txt.write("eta_constants_y = "+pars_y+"\n")
    txt.close()

move_outputs()
if RUN_ALIGNMENT or RUN_ETA:
    for run_number in run_numbers:
        chip = str(get_chip(csv_file, run_number))
        vbb = str(get_Vbb(csv_file, run_number))
        ireset = str(get_Ireset(csv_file, run_number))
        irrad = str(get_Irrad(csv_file, run_number))
        chip_status = get_status_chip(chip, vbb, irrad, ireset)

        # Check if the directory exists
        if not os.path.exists("output/"+output_dir+"/"+chip):
            # If it doesn't exist, create it
            os.makedirs("output/"+output_dir+"/"+chip)
        pitch = re.findall(r'\d+', get_chip(csv_file, run_number))[0]
        previous_runnumber, has_aligned_geometry = get_runnumber_aligned(run_number, csv_file)
        print(previous_runnumber, has_aligned_geometry)
        if RUN_ALIGNMENT:
        
            # noise
            bashCommand = f'''
            JOBSUB=/opt/corryvreckan/jobsub/jobsub.py
            ${{JOBSUB}} --zfill 6 --csv {csv_file} -o DataDir={data_dir} -o OutputDir={output_dir} -c {config_dir}/analysis_noise.conf {run_number}'''

            subprocess.run(bashCommand, shell=True, check=True, executable='/bin/bash')
            
            if RECYCLE and has_aligned_geometry:
                if str(previous_runnumber) != str(run_number):
                    bashCommand = f"cp geometry/aligned_{previous_runnumber}_DUT_step4.conf geometry/aligned_{run_number}_DUT_step4.conf"
                    subprocess.run(bashCommand, shell=True, check=True, executable='/bin/bash')
            else:
                # masking
                bashCommand = f'''
                JOBSUB=/opt/corryvreckan/jobsub/jobsub.py
                ${{JOBSUB}} --zfill 6 --csv {csv_file} -o DataDir={data_dir} -o OutputDir={output_dir} -c {config_dir}/createmask.conf {run_number}'''

                subprocess.run(bashCommand, shell=True, check=True, executable='/bin/bash')
                # prealignment
                bashCommand = f'''
                JOBSUB=/opt/corryvreckan/jobsub/jobsub.py
                ${{JOBSUB}} --zfill 6 --csv {csv_file} -o DataDir={data_dir} -o OutputDir={output_dir} -c {config_dir}/prealign.conf {run_number}'''
                
                subprocess.run(bashCommand, shell=True, check=True, executable='/bin/bash')
                # alignment of the telescope
                bashCommand = f'''
                JOBSUB=/opt/corryvreckan/jobsub/jobsub.py
                ${{JOBSUB}} --zfill 6 --csv {csv_file} -o DataDir={data_dir} -o OutputDir={output_dir} -c {config_dir}/align.conf {run_number}'''

                subprocess.run(bashCommand, shell=True, check=True, executable='/bin/bash')
                # DUT alignment
                print(pitch, type(pitch))
                pitch = int(pitch)
                spatial_cut_abs_list = [pitch*10,pitch*3,pitch*2,pitch]
                print(spatial_cut_abs_list)
                geometry_file = f"aligned_{run_number}.conf"
                step = 1

                if ADCU_THR:
                    seed_threshold = 150
                else:
                    path_noise  = "output/"+output_dir+"/"+chip+"/analysis_"+str(run_number)+"_DUT_noise.root"
                    new_seed_thresholds_in_e = get_nice_thresholds(seed_thresholds_in_e, path_noise=path_noise,chip=chip, vbb=vbb, irrad=irrad, ireset=ireset)
                    seed_thresholds_in_adc = convert_to_adc(new_seed_thresholds_in_e, chip=chip, vbb=vbb, irrad=irrad, ireset=ireset)
                    seed_threshold = seed_thresholds_in_adc[0]
                for spatial_cut_abs in spatial_cut_abs_list:
                    print(spatial_cut_abs)
                    bashCommand = f'''
                    JOBSUB=/opt/corryvreckan/jobsub/jobsub.py
                    ${{JOBSUB}} --zfill 6 --csv {csv_file} -o DataDir={data_dir} -o ThresholdSeed={seed_threshold} -o OutputDir={output_dir} -o SCA={spatial_cut_abs} -o Geometry={geometry_file} -o Step={step} -c {config_dir}/alignDUT.conf {run_number}'''

                    geometry_file = f"aligned_{run_number}_DUT_step{step}.conf"
                    subprocess.run(bashCommand, shell=True, check=True, executable='/bin/bash')
                    step += 1

#        if ADCU_THR:
#            seed_threshold = 150
#        else:
        #if has_aligned_geometry:
        #    path_noise  = "output/"+output_dir+"/"+chip+"/analysis_"+str(previous_runnumber)+"_DUT_noise.root"
        #else:
        previous_runnumber_eta_noise, has_aligned_etanoise = get_runnumber_etanoise(run_number, csv_file, chip=chip, vbb=vbb, irrad=irrad, ireset=ireset, grade=poly_grades[0])
        path_noise  = "output/"+output_dir+"/"+chip+"/analysis_"+str(previous_runnumber_eta_noise)+"_DUT_noise.root"
        new_seed_thresholds_in_e = get_nice_thresholds(seed_thresholds_in_e, path_noise=path_noise,chip=chip, vbb=vbb, irrad=irrad, ireset=ireset)
        seed_thresholds_in_adc = convert_to_adc(new_seed_thresholds_in_e, chip=chip, vbb=vbb, irrad=irrad, ireset=ireset)
        #print(seed_thresholds_in_adc)

        previous_runnumber_eta_noise, has_aligned_etanoise = get_runnumber_etanoise(run_number, csv_file, chip=chip, vbb=vbb, irrad=irrad, ireset=ireset, grade=poly_grades[0], threshold=seed_thresholds_in_adc)
        print(previous_runnumber, has_aligned_etanoise)
        if RUN_ETA:
            if not (RECYCLE and has_aligned_etanoise):
                path_noise  = "output/"+output_dir+"/"+chip+"/analysis_"+str(run_number)+"_DUT_noise.root"
                for grade in poly_grades:
                    set_pol_grade(f"{config_dir}/compute_eta.conf", grade, output_dir=output_dir)
                    if ADCU_THR:
                        #seed_thresholds_in_adc = seed_thresholds[vbb]  
                        seed_thresholds_in_adc = seed_thresholds[chip_status]           
                    else:
                        new_seed_thresholds_in_e = get_nice_thresholds(seed_thresholds_in_e, path_noise=path_noise,chip=chip, vbb=vbb, irrad=irrad, ireset=ireset)
                        seed_thresholds_in_adc = convert_to_adc(new_seed_thresholds_in_e, chip=chip, vbb=vbb, irrad=irrad, ireset=ireset)    
                    print(seed_thresholds_in_adc)
                    #a = input()
                    for seed_threshold in seed_thresholds_in_adc:

                        # Eta correction
                        bashCommand = f'''
                        JOBSUB=/opt/corryvreckan/jobsub/jobsub.py
                        ${{JOBSUB}} --zfill 6 --csv {csv_file} -o DataDir={data_dir} -o OutputDir={output_dir} -o ThresholdSeed={seed_threshold} -o ThresholdNeigh={seed_threshold} -c {config_dir}/compute_eta.conf {run_number}'''

                        subprocess.run(bashCommand, shell=True, check=True, executable='/bin/bash')

                        chip = get_chip(csv_file, run_number)
                        log_file = f"compute_eta_run_{run_number}-dut:{chip}.log"
                        os.rename(log_file, f"compute_eta_run_{run_number}-dut:{chip}-thr{seed_threshold}_pol{grade}.log")

if MERGE_ETA:

    list_of_chip_status = {}
    is_first_line = True
    with open(csv_file, 'r') as file:
        # Create a CSV reader object
        csv_reader = csv.reader(file)
        for row in csv_reader:
            if is_first_line: 
                is_first_line = False
                continue
            status_chip = get_status_chip(chip = row[2], vbb=row[3], ireset=row[4], irrad=row[5])
            if status_chip in list_of_chip_status:
                list_of_chip_status[status_chip].append(row[0])
            else:
                list_of_chip_status[status_chip] = [row[0]]

    for pol in poly_grades:
        pol = str(pol)
        for chip_status, runs in list_of_chip_status.items():
            #print(chip_status, runs)
            chip = ""
            counter = 0
            for element in chip_status:
                if element == "_":
                    counter += 1
                if counter == 2:
                    break
                chip += element
            #print(chip)
            directory = "output/"+output_dir+"/"+chip
            
            if not os.path.exists(directory):
                continue

            files = os.listdir(directory)

            threshold_list = {}
            for file in files:
                if os.path.isfile(os.path.join(directory, file)):
                    #print(file)
                    if "analysis" in file and "noise" not in file and not chip in file:
                        run_number = re.findall(r'\d+', file)[0]
                        threshold = re.findall(r'\d+', file)[-1]
                        if run_number in runs and "eta"+pol in file:
                            if threshold in threshold_list:
                                threshold_list[threshold].append(run_number)
                            else:
                                threshold_list[threshold] = [run_number]

            for thr, runs in threshold_list.items():
                print(thr,runs)
                list_of_files = ""        
                final_file = directory+"/analysis_eta"+pol+chip_status+"_thr"+thr+".root"
                fit_file = directory+"/fit_eta"+pol+chip_status+"_thr"+thr+".root"
                txt_file = directory+"/analysis_eta"+pol+chip_status+"_thr"+thr+".txt"
                for run in runs:
                    list_of_files += " "+directory+"/analysis_eta"+pol+run+"_"+thr+"_"+thr+".root"
                bashCommand = f'''hadd -f {final_file} {list_of_files}'''
                subprocess.run(bashCommand, shell=True, check=True, executable='/bin/bash')

                eta_formula_x = 'eta_formula_x = "[0]'
                eta_formula_y = 'eta_formula_y = "[0]'
                power = 0
                parameter = 0
                while grade != power:
                    power += 1
                    parameter += 1

                    if power == 1:
                        eta_formula_x += f" + [{parameter}]*x"
                        eta_formula_y += f" + [{parameter}]*x"
                    else:
                        eta_formula_x += f' + [{parameter}]*x^{power}'
                        eta_formula_y += f' + [{parameter}]*x^{power}'

                apts, pars_x, pars_y = fit_merged_tprofile(final_file, eta_formula_x, eta_formula_y, fit_file)

                write_eta_correction(apts, txt_file, eta_formula_x, eta_formula_y, pars_x, pars_y)



if RUN_ANALYSIS:
    for run_number in run_numbers:
        chip = str(get_chip(csv_file, run_number))
        vbb = str(get_Vbb(csv_file, run_number))
        ireset = str(get_Ireset(csv_file, run_number))
        irrad = str(get_Irrad(csv_file, run_number))
        chip_status = get_status_chip(chip, vbb, irrad, ireset)
        if ADCU_THR:
            #seed_thresholds_in_adc = seed_thresholds[vbb]  
            seed_thresholds_in_adc = seed_thresholds[chip_status]                      
            previous_runnumber, has_aligned_geometry = get_runnumber_aligned(run_number, csv_file)
            previous_runnumber_eta_noise, has_aligned_etanoise = get_runnumber_etanoise(run_number, csv_file, chip=chip, vbb=vbb, irrad=irrad, ireset=ireset, grade=poly_grades[0])
               
        else:
            previous_runnumber, has_aligned_geometry = get_runnumber_aligned(run_number, csv_file)
            previous_runnumber_eta_noise, has_aligned_etanoise = get_runnumber_etanoise(run_number, csv_file, chip=chip, vbb=vbb, irrad=irrad, ireset=ireset, grade=poly_grades[0])
            print(previous_runnumber_eta_noise)
            if RECYCLE:
                path_noise  = "output/"+output_dir+"/"+chip+"/analysis_"+str(previous_runnumber_eta_noise)+"_DUT_noise.root"
            else:
                path_noise  = "output/"+output_dir+"/"+chip+"/analysis_"+str(run_number)+"_DUT_noise.root"
            new_seed_thresholds_in_e = get_nice_thresholds(seed_thresholds_in_e, path_noise=path_noise,chip=chip, vbb=vbb, irrad=irrad, ireset=ireset)
            seed_thresholds_in_adc = convert_to_adc(new_seed_thresholds_in_e, chip=chip, vbb=vbb, irrad=irrad, ireset=ireset)

        directory = "output/"+output_dir+"/"+chip
        print(chip_status)
        
        for method in methods:
            for seed_threshold in seed_thresholds_in_adc:
                print(seed_threshold)
                scs = 1
                if method=="window":
                    scs = 0                
                if method=="cluster_eta":
                    # Open the original file for reading
                    with open(config_dir+'/analysis.conf', 'r') as original_file:
                        # Read the contents of the file into memory
                        file_contents = original_file.read()

                    # Open a new file for writing
                    with open(config_dir+'/analysis_tmp.conf', 'w') as new_file:
                        # Write the contents of the original file to the new file
                        new_file.write(file_contents)

                    chip = get_chip(csv_file, run_number)
                    for grade in poly_grades:
                        grade = str(grade)
                        log_file = directory+"/analysis_eta"+grade+chip_status+"_thr"+str(seed_threshold)+".txt"
                        if not USE_MERGED_ETA:
                            if RECYCLE:
                                log_file = f"compute_eta_run_{previous_runnumber_eta_noise}-dut:{chip}-thr{seed_threshold}_pol{grade}.log"
                            else:
                                log_file = f"compute_eta_run_{run_number}-dut:{chip}-thr{seed_threshold}_pol{grade}.log"
                        print(log_file)
                        apply_eta_contants(log_file, config_dir+'/analysis_tmp.conf', grade, output_dir=output_dir)
                        bashCommand = f'''
                        JOBSUB=/opt/corryvreckan/jobsub/jobsub.py
                        ${{JOBSUB}} --zfill 6 --csv {csv_file} -o DataDir={data_dir} -o SCS={scs}  -o OutputDir={output_dir} -o ThresholdSeed={seed_threshold} -o ThresholdNeigh={seed_threshold} -o Method=cluster -c {config_dir}/analysis_tmp.conf {run_number}'''

                        subprocess.run(bashCommand, shell=True, check=True, executable='/bin/bash')
                else:
                    bashCommand = f'''
                    JOBSUB=/opt/corryvreckan/jobsub/jobsub.py
                    ${{JOBSUB}} --zfill 6 --csv {csv_file} -o DataDir={data_dir} -o SCS={scs}  -o OutputDir={output_dir} -o ThresholdSeed={seed_threshold} -o ThresholdNeigh={seed_threshold} -o Method={method} -c {config_dir}/analysis.conf {run_number}'''
                    subprocess.run(bashCommand, shell=True, check=True, executable='/bin/bash')
                


move_outputs()
