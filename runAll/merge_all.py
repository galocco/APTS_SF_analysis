#based on chatGPTs
import subprocess
import os
import os.path
import re
import csv


csv_file = "data/runsSPSMay23.csv"
data_dir = "data/2023-05_SPS"
config_dir = "configs/2023-05_SPS"
output_dir = "2023-05_SPS" #dont put output NOT necessary
method_list = ["binary","cluster","cluster_eta5"]

def get_status_chip(chip, vbb, irrad="None", ireset="1"):
    status_chip = chip+"_"+vbb+"V"
    if irrad != "None":
        status_chip += "_"+irrad
    if ireset != "1":
        status_chip += "_IR"+ireset
        
    return status_chip

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

for method in method_list:
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
        files = os.listdir(directory)

        threshold_list = {}
        for file in files:
            if os.path.isfile(os.path.join(directory, file)):
                #print(file)
                if "analysis" in file and "noise" not in file and not chip in file:
                    run_number = re.findall(r'\d+', file)[0]
                    threshold = re.findall(r'\d+', file)[-1]
                    if run_number in runs and method in file:
                        if threshold in threshold_list:
                            threshold_list[threshold].append(run_number)
                        else:
                            threshold_list[threshold] = [run_number]

        list_of_files2 = []
        thresholds = []
        #print(chip_status)
        if "4.8V_1.00E+15" not in chip_status:
            continue
        for thr, runs in threshold_list.items():
            print(thr,runs)
            list_of_files = ""        
            final_file = directory+"/analysis_"+chip_status+"_"+method+"_thr"+thr+".root"
            for run in runs:
                list_of_files += " "+directory+"/analysis_"+run+"_"+method+"_"+thr+"_"+thr+".root"
            bashCommand = f'''hadd -f {final_file} {list_of_files}'''
            #subprocess.run(bashCommand, shell=True, check=True, executable='/bin/bash')
            print(bashCommand)
            list_of_files2.append("/home/giacomo/its-corryvreckan-tools/"+directory+"/analysis_"+chip_status+"_"+method+"_thr"+thr+".root")
            thresholds.append(float(thr))
        sorted_list = sorted(list_of_files2, key=lambda x: thresholds[list_of_files2.index(x)])
        f = open(directory+"/"+chip_status+"_"+method+".txt", "w")

        f.write('[\n')
        for sort in sorted_list:
            if sort != sorted_list[-1]:
                f.write('   "'+sort+'",\n')
            else:
                f.write('   "'+sort+'"\n')
        f.write('],\n')
        
