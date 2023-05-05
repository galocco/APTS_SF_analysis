import subprocess
import argparse
import os
import re
import csv

run_numbers = [184224042230505002728,184224043230505021904,184224044230505044337] #list of runs
#list of runs for which we can copy the aligned geometry
copy_list = {
                "184224042230505002728" : "184224041230504224047",
                "184224043230505021904" : "184224041230504224047",
                "184224044230505044337" : "184224041230504224047"
            }
seed_thresholds = [0,40,70,80,100,120,140,160,180,200,250]
poly_grades = [5]
methods = ["cluster"]#"window","binary","cluster"]
csv_file = "data/runsPSMay23.csv"
data_dir = "data/2023-05_PS"
config_dir = "configs/2023-05_PS/B1"
output_dir = "2023-05_PS" #dont put output NOT necessary
if False:
    csv_file = "data/runsSPSOctober22.csv"
    data_dir = "data/SPSOctober22/B1"
    config_dir = "configs/SPSOctober22/B1"

parser = argparse.ArgumentParser()
parser.add_argument(
    '-al', '--alignment', help='Use fit compute the resolution and mean', action='store_true')
parser.add_argument(
    '-an', '--analysis', help='Use fit compute the resolution and mean', action='store_true')
parser.add_argument(
    '-e', '--eta', help='Use fit compute the resolution and mean', action='store_true')
args = parser.parse_args()
RUN_ALIGNMENT = args.alignment
RUN_ANALYSIS = args.analysis
RUN_ETA = args.eta

def apply_eta_contants(log_file, config_file, grade = 5):
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
    lines[6] = f'histogram_file = "SPSOctober22/B1/@DUT@/analysis_eta{grade}_@RunNumber@_@Method@_@ThresholdNeigh@_@ThresholdSeed@.root"\n'
    lines.insert(7, "")
    lines.insert(40, eta_correction)

    # Open the file in write mode and write the modified list to the file
    with open(config_file, 'w') as file:
        file.writelines(lines)

def set_pol_grade(config_file, grade, odd=True):
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

    lines[6] = f'histogram_file         = "SPSOctober22/B1/@DUT@/analysis_eta{grade}_@RunNumber@_@ThresholdNeigh@_@ThresholdSeed@.root"\n'

    lines[65] = eta_formula_x +'"\n'
    lines[66] = eta_formula_y +'"\n'

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

if RUN_ALIGNMENT:
    for run_number in run_numbers:
        chip = str(get_chip(csv_file, run_number))

        # Check if the directory exists
        if not os.path.exists(output_dir+"/"+chip):
            # If it doesn't exist, create it
            os.makedirs(output_dir+"/"+chip)

        pitch = re.findall(r'\d+', get_chip(csv_file, run_number))[0]
        # masking
        bashCommand = f'''
        JOBSUB=/opt/corryvreckan/jobsub/jobsub.py
        ${{JOBSUB}} --zfill 6 --csv {csv_file} -o DataDir={data_dir} -o OutputDir={output_dir} -c {config_dir}/createmask.conf {run_number}'''

        subprocess.run(bashCommand, shell=True, check=True, executable='/bin/bash')
        if str(run_number) not in copy_list:

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
            spatial_cut_abs_list = [pitch*100,pitch*3,pitch*2,pitch]
            geometry_file = f"aligned_{run_number}.conf"
            step = 1
            for spatial_cut_abs in spatial_cut_abs_list:
                bashCommand = f'''
                JOBSUB=/opt/corryvreckan/jobsub/jobsub.py
                ${{JOBSUB}} --zfill 6 --csv {csv_file} -o DataDir={data_dir} -o OutputDir={output_dir} -o SCA={spatial_cut_abs} -o Geometry={geometry_file} -o Step={step} -c {config_dir}/alignDUT.conf {run_number}'''

                geometry_file = f"aligned_{run_number}_DUT_step{step}.conf"
                subprocess.run(bashCommand, shell=True, check=True, executable='/bin/bash')
                step += 1
            
        else:
            bashCommand = f"cp geometry/aligned_{copy_list[str(run_number)]}_DUT_step4.conf geometry/aligned_{run_number}_DUT_step4.conf"
            subprocess.run(bashCommand, shell=True, check=True, executable='/bin/bash')

        if RUN_ETA:
            for grade in poly_grades:
                set_pol_grade(f"{config_dir}/compute_eta.conf", grade)
                for seed_threshold in seed_thresholds:
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
        for method in methods:
            for seed_threshold in seed_thresholds:
                scs = 1
                if method=="window":
                    scs = 0
                bashCommand = f'''
                JOBSUB=/opt/corryvreckan/jobsub/jobsub.py
                ${{JOBSUB}} --zfill 6 --csv {csv_file} -o DataDir={data_dir} -o SCS={scs}  -o OutputDir={output_dir} -o ThresholdSeed={seed_threshold} -o ThresholdNeigh={seed_threshold} -o Method={method} -c {config_dir}/analysis.conf {run_number}'''
                subprocess.run(bashCommand, shell=True, check=True, executable='/bin/bash')
                
                if method=="cluster" and RUN_ETA:
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
                        apply_eta_contants(log_file, config_dir+'/analysis_tmp.conf', grade)
                        bashCommand = f'''
                        JOBSUB=/opt/corryvreckan/jobsub/jobsub.py
                        ${{JOBSUB}} --zfill 6 --csv {csv_file} -o DataDir={data_dir} -o SCS={scs}  -o OutputDir={output_dir} -o ThresholdSeed={seed_threshold} -o ThresholdNeigh={seed_threshold} -o Method={method} -c {config_dir}/analysis_tmp.conf {run_number}'''

                        subprocess.run(bashCommand, shell=True, check=True, executable='/bin/bash')
