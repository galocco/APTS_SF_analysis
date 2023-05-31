#based on chatGPTs
import subprocess
import argparse
import os
import os.path
import re
import csv
import utils
from ROOT import TFile

#list of runs
run_numbers =    [
207104607230521104622,
207104608230521115019,
207134922230521134937,
207134923230521144602
                ]

#list of thresholds in electrons
seed_thresholds_in_e = [60,80,100,120,140,160,180,200,250,300]
#list of the threshold in ADCu if you want to use yours
#add an item with the Vbb and the list 
seed_thresholds = {
                    "0.0": [40,50, 60,80,100,120,140],
                    "1.2": [70,80,100,120,140,160,180,200,250],
                    "4.8": [160,180,200,250,300,350,400]
                    }
#polynomial grade for the eta correction. 5 is fine
poly_grades = [5]
#list clustering methods
#same names as in ClusteringAnalog. Only cluster_eta is different, use it to run the analysis with cluster + eta correction
methods = ["cluster_eta","binary"]#"window","binary","cluster"]
#csv file with the run list
csv_file = "data/runsSPSMay23.csv"
#directory with the data
data_dir = "data/2023-05_SPS"
#directory with the configs files
config_dir = "configs/2023-05_SPS"
#directory for the output
output_dir = "2023-05_SPS" #no need for output

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

args = parser.parse_args()
RUN_ALIGNMENT = args.alignment
RUN_ANALYSIS = args.analysis
RUN_ETA = args.eta
ADCU_THR = args.thr
RECYCLE = args.recy


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

def set_pol_grade(config_file, grade, odd=True, output_dir = "SPSOctober22/B1"):
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
    new_chip = ""
    for element in range(0, len(chip)):
        if chip[element] == "B":
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

    status_chip = get_status_chip(chip, vbb, irrad, ireset)
    root_file = TFile(path_noise, "READ")
    subdir = root_file.Get("EventLoaderEUDAQ2")
    key_list = subdir.GetListOfKeys()
    for key in key_list:
        if key.GetClassName() == "TDirectoryFile" and "APTS" in key.GetName():
            apts = key.GetName()
            break

    print(apts)
    noise_values = root_file.Get(
        "EventLoaderEUDAQ2/"+apts+"/hPixelRawValues")
    print("plotting above ", noise_values.GetStdDev()*nsigma_noise, " ADCu")

    eThrLimit = noise_values.GetStdDev()*nsigma_noise*100/utils.hundredElectronToADCu[status_chip]
    root_file.Close()
    rejected_list = []
    if reject_below_noise:
        for thr in threshold_list:
            #print(thr)
            if thr < eThrLimit:
                #print("rejected", thr)
                rejected_list.append(thr)
    for rej in rejected_list:
        threshold_list.remove(rej)
    threshold_list.insert(0, eThrLimit+1)
    
    return threshold_list

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
            if row[1] == ideal_geometry:
                if os.path.isfile(f"geometry/aligned_{row[0]}_DUT_step4.conf"):
                    return row[0], True
    return None, False

if RUN_ALIGNMENT or RUN_ETA:
    for run_number in run_numbers:
        chip = str(get_chip(csv_file, run_number))
        vbb = str(get_Vbb(csv_file, run_number))
        ireset = str(get_Ireset(csv_file, run_number))
        irrad = str(get_Irrad(csv_file, run_number))

        # Check if the directory exists
        if not os.path.exists("output/"+output_dir+"/"+chip):
            # If it doesn't exist, create it
            os.makedirs("output/"+output_dir+"/"+chip)

        pitch = re.findall(r'\d+', get_chip(csv_file, run_number))[0]
        if RUN_ALIGNMENT:
            # noise
            bashCommand = f'''
            JOBSUB=/opt/corryvreckan/jobsub/jobsub.py
            ${{JOBSUB}} --zfill 6 --csv {csv_file} -o DataDir={data_dir} -o OutputDir={output_dir} -c {config_dir}/analysis_noise.conf {run_number}'''

            subprocess.run(bashCommand, shell=True, check=True, executable='/bin/bash')
            # masking
            bashCommand = f'''
            JOBSUB=/opt/corryvreckan/jobsub/jobsub.py
            ${{JOBSUB}} --zfill 6 --csv {csv_file} -o DataDir={data_dir} -o OutputDir={output_dir} -c {config_dir}/createmask.conf {run_number}'''

            subprocess.run(bashCommand, shell=True, check=True, executable='/bin/bash')
                
            previous_runnumber, has_aligned_geometry = get_runnumber_aligned(run_number, csv_file)
            if RECYCLE and has_aligned_geometry:
                if str(previous_runnumber) != str(run_number):
                    bashCommand = f"cp geometry/aligned_{previous_runnumber}_DUT_step4.conf geometry/aligned_{run_number}_DUT_step4.conf"
                    subprocess.run(bashCommand, shell=True, check=True, executable='/bin/bash')
            else:
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
                spatial_cut_abs_list = [pitch*4,pitch*3,pitch*2,pitch]
                geometry_file = f"aligned_{run_number}.conf"
                step = 1
                for spatial_cut_abs in spatial_cut_abs_list:
                    bashCommand = f'''
                    JOBSUB=/opt/corryvreckan/jobsub/jobsub.py
                    ${{JOBSUB}} --zfill 6 --csv {csv_file} -o DataDir={data_dir} -o OutputDir={output_dir} -o SCA={spatial_cut_abs} -o Geometry={geometry_file} -o Step={step} -c {config_dir}/alignDUT.conf {run_number}'''

                    geometry_file = f"aligned_{run_number}_DUT_step{step}.conf"
                    subprocess.run(bashCommand, shell=True, check=True, executable='/bin/bash')
                    step += 1

        if RUN_ETA:
            for grade in poly_grades:
                set_pol_grade(f"{config_dir}/compute_eta.conf", grade, output_dir=output_dir)
                if ADCU_THR:
                    seed_thresholds_in_adc = seed_thresholds[vbb]           
                else:
                    if has_aligned_geometry:
                        path_noise  = "output/"+output_dir+"/"+chip+"/analysis_"+str(previous_runnumber)+"_DUT_noise.root"
                    else:
                        path_noise  = "output/"+output_dir+"/"+chip+"/analysis_"+str(run_number)+"_DUT_noise.root"
                    new_seed_thresholds_in_e = get_nice_thresholds(seed_thresholds_in_e, path_noise=path_noise,chip=chip, vbb=vbb, irrad=irrad, ireset=ireset)
                    seed_thresholds_in_adc = convert_to_adc(new_seed_thresholds_in_e, chip=chip, vbb=vbb, irrad=irrad, ireset=ireset)
                for seed_threshold in seed_thresholds_in_adc:
                    # Eta correction
                    bashCommand = f'''
                    JOBSUB=/opt/corryvreckan/jobsub/jobsub.py
                    ${{JOBSUB}} --zfill 6 --csv {csv_file} -o DataDir={data_dir} -o OutputDir={output_dir} -o ThresholdSeed={seed_threshold} -o ThresholdNeigh={seed_threshold} -c {config_dir}/compute_eta.conf {run_number}'''

                    subprocess.run(bashCommand, shell=True, check=True, executable='/bin/bash')

                    chip = get_chip(csv_file, run_number)
                    log_file = f"compute_eta_run_{run_number}-dut:{chip}.log"
                    os.rename(log_file, f"compute_eta_run_{run_number}-dut:{chip}-thr{seed_threshold}_pol{grade}.log")

if RUN_ANALYSIS:
    for run_number in run_numbers:
        chip = str(get_chip(csv_file, run_number))
        vbb = str(get_Vbb(csv_file, run_number))
        ireset = str(get_Ireset(csv_file, run_number))
        irrad = str(get_Irrad(csv_file, run_number))
        if ADCU_THR:
            seed_thresholds_in_adc = seed_thresholds[vbb]           
        else:
            previous_runnumber, has_aligned_geometry = get_runnumber_aligned(run_number, csv_file)
            if has_aligned_geometry:
                path_noise  = "output/"+output_dir+"/"+chip+"/analysis_"+str(previous_runnumber)+"_DUT_noise.root"
            else:
                path_noise  = "output/"+output_dir+"/"+chip+"/analysis_"+str(run_number)+"_DUT_noise.root"
            new_seed_thresholds_in_e = get_nice_thresholds(seed_thresholds_in_e, path_noise=path_noise,chip=chip, vbb=vbb, irrad=irrad, ireset=ireset)
            seed_thresholds_in_adc = convert_to_adc(new_seed_thresholds_in_e, chip=chip, vbb=vbb, irrad=irrad, ireset=ireset)

        for method in methods:
            for seed_threshold in seed_thresholds_in_adc:
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
                        log_file = f"compute_eta_run_{run_number}-dut:{chip}-thr{seed_threshold}_pol{grade}.log"
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

