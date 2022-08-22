import pandas as pd
import os
import re
import shutil
import math
from tempfile import mkstemp
from shutil import move, copymode
from os import fdopen, remove

#function to modify a file
def replace(file_path, pattern, subst):
    #Create temp file
    fh, abs_path = mkstemp()
    with fdopen(fh,'w') as new_file:
        with open(file_path) as old_file:
            for line in old_file:
                new_file.write(line.replace(pattern, subst))
    #Copy the file permissions from the old file to the new file
    copymode(file_path, abs_path)
    #Remove original file
    remove(file_path)
    #Move new file
    move(abs_path, file_path)

#if F
rewrite = False

data= pd.read_csv("/home/giacomo/Downloads/run_list_Log_Apr22.csv")
data = data.query("Quality=='good' and Downloaded=='yes'")

directory = "/home/giacomo/test/"
if not os.path.exists(directory):
    os.makedirs(directory)
list_of_dirs = ["config","output","geometry"]
for di in list_of_dirs:
    if not os.path.exists(directory+di):
        os.makedirs(directory+di)

for row in data.itertuples():
    run_number = row.Run.replace('.raw','')
    chip = row.Chip.replace('run','').replace('.raw','')
    vbb = row.Vbb
    threshold = row.Threshold if math.isnan(row.Threshold) else 50
    print(run_number,chip,vbb)
    for di in list_of_dirs:
        pixel_pitch = re.findall(r'\d+', chip)[0]
        spatial_cut_abs = [int(pixel_pitch)*4,int(pixel_pitch)*3,int(pixel_pitch)*2,int(pixel_pitch)]
        chip_dir = directory+di+"/"+chip+"/"
        if not os.path.exists(chip_dir):
            os.makedirs(chip_dir)
        run_dir = chip_dir + run_number
        if not os.path.exists(run_dir):
            os.makedirs(run_dir)
        for cut in spatial_cut_abs:
            if not os.path.exists(run_dir+'/alignDUT_sca_'+str(cut)+'.conf') or rewrite:
                shutil.copyfile('/home/giacomo/alignDUT.conf', run_dir+'/alignDUT_sca_'+str(cut)+'.conf')
                replace(run_dir+'/alignDUT_sca_'+str(cut)+'.conf','spatial_cut_abs = 100um,100um','spatial_cut_abs='+str(cut)+'um,'+str(cut)+'um')
                replace(run_dir+'/alignDUT_sca_'+str(cut)+'.conf','detectors_file = "geometry/dummy.conf"','detectors_file = "geometry/align_'+str(run_number)+'.conf"')
                replace(run_dir+'/alignDUT_sca_'+str(cut)+'.conf','detectors_file_updated = "geometry/dummy.conf"','detectors_file_updated = "geometry/align_'+str(run_number)+'.conf"')
                replace(run_dir+'/alignDUT_sca_'+str(cut)+'.conf','histogram_file = "dummy.root"','histogram_file = "align_'+str(run_number)+'.root"')
        
        if not os.path.exists(run_dir+'/prealign.conf') or rewrite:
            shutil.copyfile('/home/giacomo/prealignDUT.conf', run_dir+'/prealignDUT.conf')
            replace(run_dir+'/prealignDUT.conf','detectors_file = "geometry/dummy.conf"','detectors_file = "geometry/prealign.conf"')
            replace(run_dir+'/prealignDUT.conf','detectors_file_updated = "geometry/dummy.conf"','detectors_file_updated = "geometry/prealign.conf"')
            replace(run_dir+'/prealignDUT.conf','histogram_file = "dummy.root"','histogram_file = "prealign.root"')
        
        if not os.path.exists(run_dir+'/analyseDUT.conf') or rewrite:
            shutil.copyfile('/home/giacomo/analyseDUT.conf', run_dir+'/analyseDUT.conf')
            replace(run_dir+'/analyseDUT.conf','detectors_file = "geometry/dummy.conf"','detectors_file = "geometry/prealign.conf"')
            replace(run_dir+'/analyseDUT.conf','detectors_file_updated = "geometry/dummy.conf"','detectors_file_updated = "geometry/prealign.conf"')
            replace(run_dir+'/analyseDUT.conf','histogram_file = "dummy.root"','histogram_file = "prealign.root"')
        