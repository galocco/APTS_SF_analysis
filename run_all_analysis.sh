#!/bin/sh
JOBSUB=/opt/corryvreckan/jobsub/jobsub.py

cp EventLoaderEUDAQ2.cpp /opt/corryvreckan/src/modules/EventLoaderEUDAQ2/
cp AnalysisEfficiency.cpp /opt/corryvreckan/src/modules/AnalysisEfficiency/
cd /opt/corryvreckan/build/ && make install -j12 && cd /local

#loop over the different pixel pitches
for pitch in 15
do
frame_window=0

#loop over the window frame
for frame in  "if ((imin < 2) || (imin > 200)){"  #"if ((imin < 99) || (imin > 105)){" #"if ((imin < 106) || (imin > 200)){" "  if ( ((imin < 50) || (imin > 200)) || ((imin > 99) \&\& (imin < 105)) ){"
do

#loop over the baseline frame
for nb in 1
do
frame_window=$((frame_window+1))

cp APTSRawEvent2StdEventConverter.cc APTSRawEvent2StdEventConverter_tmp.cc
sed -i "s/int nb=98;/int nb=${nb};/g"  APTSRawEvent2StdEventConverter_tmp.cc

sed -i "s/if ((imin < 99) || (imin > 105)){/ ${frame}/g"  APTSRawEvent2StdEventConverter_tmp.cc

cp APTSRawEvent2StdEventConverter_tmp.cc /opt/eudaq2/user/ITS3/module/src/APTSRawEvent2StdEventConverter.cc 
cd /opt/eudaq2/build/ && make install -j12 && cd /local

#rm APTSRawEvent2StdEventConverter_tmp.cc

#loop over the spatial_cut_abs
for spatial_cut_abs in 20 #16 17 18 19 20 21 22 23 24 25 30 40
do

#loop over the thresholds of the seed
for threshold_seed in 60 70 80 100 120 140 160 180 200
do

#loop over the inpixel_cut_edge
for inpixel_cut_edge in 0
do

cp configs/APTS_0000${pitch}/analyseDUT.conf configs/APTS_0000${pitch}/analyseDUT_${pitch}_thr_${threshold_seed}_sca_${spatial_cut_abs}_ice_${inpixel_cut_edge}_nb_${nb}_105.conf
#let "sca=pitch+5"
sed -i "s/threshold_seed=80/threshold_seed=${threshold_seed}/g" configs/APTS_0000${pitch}/analyseDUT_${pitch}_thr_${threshold_seed}_sca_${spatial_cut_abs}_ice_${inpixel_cut_edge}_nb_${nb}_105.conf
sed -i "s/spatial_cut_abs = 20um,20um/spatial_cut_abs = ${spatial_cut_abs}um,${spatial_cut_abs}um/g" configs/APTS_0000${pitch}/analyseDUT_${pitch}_thr_${threshold_seed}_sca_${spatial_cut_abs}_ice_${inpixel_cut_edge}_nb_${nb}_105.conf
sed -i "s/inpixel_cut_edge=0um,0um/inpixel_cut_edge = ${inpixel_cut_edge}um,${inpixel_cut_edge}um/g" configs/APTS_0000${pitch}/analyseDUT_${pitch}_thr_${threshold_seed}_sca_${spatial_cut_abs}_ice_${inpixel_cut_edge}_nb_${nb}_105.conf
#sed -i "s/spatial_cut_sensoredge=1/spatial_cut_sensoredge=0/g" configs/APTS_0000${pitch}/analyseDUT_${pitch}_thr_${threshold_seed}_sca_${spatial_cut_abs}_ice_${inpixel_cut_edge}_nb_${nb}_105.conf

${JOBSUB} --zfill 6 --csv data/runs.csv -o DataDir=data -o NumberOfEvents=-1 -c configs/APTS_0000${pitch}/analyseDUT_${pitch}_thr_${threshold_seed}_sca_${spatial_cut_abs}_ice_${inpixel_cut_edge}_nb_${nb}_105.conf  0000${pitch}

#rm configs/APTS_0000${pitch}/analyseDUT_${pitch}_thr_${threshold_seed}_sca_${spatial_cut_abs}_ice_${inpixel_cut_edge}_nb_${nb}_105.conf

mv output/run0000${pitch}/analyseDUT_0000${pitch}.root output/run0000${pitch}/analyseDUT_${pitch}_thr_${threshold_seed}_sca_${spatial_cut_abs}_ice_${inpixel_cut_edge}_nb_${nb}_200.root

done
done
done
done
done
done