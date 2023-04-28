import subprocess
import argparse
import os
import re
import csv

run_numbers = [413221453221013042711]#417165943221016165948
seed_thresholds = [70,80,100,120,140,160,180,200,250]
methods = ["binary","binary","cluster","window"]
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

def apply_eta_contants(log_file, config_file):
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
    lines[6] = 'histogram_file = "SPSOctober22/B1/@DUT@/analysis_eta_@RunNumber@_@Method@_@ThresholdNeigh@_@ThresholdSeed@.root"\n'
    lines.insert(7, "")
    lines.insert(40, eta_correction)

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
                return row[4]
        
    return None

if RUN_ALIGNMENT:
    for run_number in run_numbers:
        pitch = re.findall(r'\d+', get_chip(csv_file, run_number))[0]
        # masking
        bashCommand = f'''
        JOBSUB=/opt/corryvreckan/jobsub/jobsub.py
        ${{JOBSUB}} --zfill 6 --csv {csv_file} -o DataDir={data_dir} -c {config_dir}/createmask.conf {run_number}'''

        subprocess.run(bashCommand, shell=True, check=True, executable='/bin/bash')
        # prealignment
        bashCommand = f'''
        JOBSUB=/opt/corryvreckan/jobsub/jobsub.py
        ${{JOBSUB}} --zfill 6 --csv {csv_file} -o DataDir={data_dir} -c {config_dir}/prealign.conf {run_number}'''

        subprocess.run(bashCommand, shell=True, check=True, executable='/bin/bash')
        # alignment of the telescope
        bashCommand = f'''
        JOBSUB=/opt/corryvreckan/jobsub/jobsub.py
        ${{JOBSUB}} --zfill 6 --csv {csv_file} -o DataDir={data_dir} -c {config_dir}/align.conf {run_number}'''

        subprocess.run(bashCommand, shell=True, check=True, executable='/bin/bash')
        # DUT alignment
        spatial_cut_abs_list = [pitch*4,pitch*3,pitch*2,pitch]
        geometry_file = f"aligned_{run_number}.conf"
        step = 1
        for spatial_cut_abs in spatial_cut_abs_list:
            bashCommand = f'''
            JOBSUB=/opt/corryvreckan/jobsub/jobsub.py
            ${{JOBSUB}} --zfill 6 --csv {csv_file} -o DataDir={data_dir} -o Geometry={geometry_file} -o Step={step} -c {config_dir}/alignDUT.conf {run_number}'''

            geometry_file = f"aligned_{run_number}_DUT_step{step}.conf"
            subprocess.run(bashCommand, shell=True, check=True, executable='/bin/bash')
            step += 1
        

        for seed_threshold in seed_thresholds:
            # Eta correction
            bashCommand = f'''
            JOBSUB=/opt/corryvreckan/jobsub/jobsub.py
            ${{JOBSUB}} --zfill 6 --csv {csv_file} -o DataDir={data_dir} -o ThresholdSeed={seed_threshold} -o ThresholdNeigh={seed_threshold} -c {config_dir}/compute_eta.conf {run_number}'''

            subprocess.run(bashCommand, shell=True, check=True, executable='/bin/bash')

            chip = get_chip(csv_file, run_number)
            log_file = f"compute_eta_run_{run_number}-dut:{chip}.log"
            os.rename(log_file, f"compute_eta_run_{run_number}-dut:{chip}-thr{seed_threshold}_binary.log")
    
if RUN_ANALYSIS:
    for run_number in run_numbers:
        for method in methods:
            for seed_threshold in seed_thresholds:
                scs = 1
                if method=="window":
                    scs = 0
                bashCommand = f'''
                JOBSUB=/opt/corryvreckan/jobsub/jobsub.py
                ${{JOBSUB}} --zfill 6 --csv {csv_file} -o DataDir={data_dir} -o SCS={scs} -o ThresholdSeed={seed_threshold} -o ThresholdNeigh={seed_threshold} -o Method={method} -c {config_dir}/analysis.conf {run_number}'''
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
                    log_file = f"compute_eta_run_{run_number}-dut:{chip}-thr{seed_threshold}.log"
                    apply_eta_contants(log_file, config_dir+'/analysis_tmp.conf')
                    bashCommand = f'''
                    JOBSUB=/opt/corryvreckan/jobsub/jobsub.py
                    ${{JOBSUB}} --zfill 6 --csv {csv_file} -o DataDir={data_dir} -o SCS={scs} -o ThresholdSeed={seed_threshold} -o ThresholdNeigh={seed_threshold} -o Method={method} -c {config_dir}/analysis_tmp.conf {run_number}'''

                    subprocess.run(bashCommand, shell=True, check=True, executable='/bin/bash')