import os
import subprocess

dict_pitch = {
    "10": [
            [
                "80 120 260",#threshold_seed
                "10 15 20",#spatial_cut_abs
                "0" #inpixel_cut_edge
            ],
            [
                "80",#threshold_seed
                "10 15 20 25",#spatial_cut_abs
                "0" #inpixel_cut_edge
            ],
          ]
}

for val in dict_pitch.items():
    print("pitch: ",val[0])
    for v2 in val[1]:
        print("------")
        for v3 in v2:
            print(v3)
    print("==========")

bash_ini = '''
            cp EventLoaderEUDAQ2.cpp /opt/corryvreckan/src/modules/EventLoaderEUDAQ2/
            cp AnalysisEfficiency.cpp /opt/corryvreckan/src/modules/AnalysisEfficiency/
            cd /opt/corryvreckan/build/ && make install -j12 && cd /local
           '''
subprocess.check_output(bash_ini, shell=True)
bash_code = '''

JOBSUB=/opt/corryvreckan/jobsub/jobsub.py
frame_window=0

#loop over the window frame
for frame in  "if ((imin < 2) || (imin > 200))"
do

#loop over the baseline frame
for nb in 1
do
frame_window=$((frame_window+1))

cp APTSRawEvent2StdEventConverter.cc APTSRawEvent2StdEventConverter_tmp.cc
sed -i "s/int nb=98;/int nb=${{nb}};/g"  APTSRawEvent2StdEventConverter_tmp.cc

sed -i "s/if ((imin < 99) || (imin > 105)) / ${{frame}}/g"  APTSRawEvent2StdEventConverter_tmp.cc

cp APTSRawEvent2StdEventConverter_tmp.cc /opt/eudaq2/user/ITS3/module/src/APTSRawEvent2StdEventConverter.cc 
cd /opt/eudaq2/build/ && make install -j12 && cd /local

#rm APTSRawEvent2StdEventConverter_tmp.cc

#loop over the spatial_cut_abs
for spatial_cut_abs in {sca_list} 
do

#loop over the thresholds of the seed
for threshold_seed in {thr_list}
do

#loop over the inpixel_cut_edge
for inpixel_cut_edge in {ice_list}
do

cp configs/APTS_0000{pitch}/analyseDUT.conf configs/APTS_0000{pitch}/analyseDUT_{pitch}_thr_${{threshold_seed}}_sca_${{spatial_cut_abs}}_ice_${{inpixel_cut_edge}}_nb_${{nb}}_105.conf
#let "sca=pitch+5"
sed -i "s/threshold_seed=80/threshold_seed=${{threshold_seed}}/g" configs/APTS_0000{pitch}/analyseDUT_{pitch}_thr_${{threshold_seed}}_sca_${{spatial_cut_abs}}_ice_${{inpixel_cut_edge}}_nb_${{nb}}_105.conf
sed -i "s/spatial_cut_abs = 20um,20um/spatial_cut_abs = ${{spatial_cut_abs}}um,${{spatial_cut_abs}}um/g" configs/APTS_0000{pitch}/analyseDUT_{pitch}_thr_${{threshold_seed}}_sca_${{spatial_cut_abs}}_ice_${{inpixel_cut_edge}}_nb_${{nb}}_105.conf
sed -i "s/inpixel_cut_edge=0um,0um/inpixel_cut_edge = ${{inpixel_cut_edge}}um,${{inpixel_cut_edge}}um/g" configs/APTS_0000{pitch}/analyseDUT_{pitch}_thr_${{threshold_seed}}_sca_${{spatial_cut_abs}}_ice_${{inpixel_cut_edge}}_nb_${{nb}}_105.conf

${{JOBSUB}} --zfill 6 --csv data/runs.csv -o DataDir=data -o NumberOfEvents=100 -c configs/APTS_0000{pitch}/analyseDUT_{pitch}_thr_${{threshold_seed}}_sca_${{spatial_cut_abs}}_ice_${{inpixel_cut_edge}}_nb_${{nb}}_105.conf  0000{pitch}

rm configs/APTS_0000{pitch}/analyseDUT_{pitch}_thr_${{threshold_seed}}_sca_${{spatial_cut_abs}}_ice_${{inpixel_cut_edge}}_nb_${{nb}}_105.conf

#mv output/run0000{pitch}/analyseDUT_0000{pitch}.root output/run0000{pitch}/analyseDUT_{pitch}_thr_${{threshold_seed}}_sca_${{spatial_cut_abs}}_ice_${{inpixel_cut_edge}}_nb_${{nb}}_200.root

done
done
done
done
done
'''

for val in dict_pitch.items():
    for settings in val[1]:
        os.system(bash_code.format(pitch = val[0], thr_list = settings[0], sca_list = settings[1], ice_list = settings[2]))